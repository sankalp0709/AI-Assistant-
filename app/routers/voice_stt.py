import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

import whisper   # whisper is installed from openai-whisper

router = APIRouter()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice_stt")

# Supported formats
SUPPORTED_MIMETYPES = {
    "audio/wav": "wav",
    "audio/mpeg": "mp3",
    "audio/mp4": "m4a",
    "audio/x-m4a": "m4a"
}

# MAX size 25MB
MAX_FILE_SIZE = 25 * 1024 * 1024

# Global Whisper model cache
_whisper_model = None


def load_whisper_model(model_name: str = "base"):
    """
    Loads whisper model only once (global cache)
    """
    global _whisper_model

    if _whisper_model is None:
        try:
            logger.info(f"Loading Whisper model: {model_name}")
            _whisper_model = whisper.load_model(model_name)
            logger.info("Whisper loaded successfully.")
        except Exception as e:
            logger.error(f"Whisper load error: {e}")
            raise HTTPException(status_code=500, detail="Failed to load Whisper model")

    return _whisper_model


class STTResponse(BaseModel):
    text: str
    language: str
    confidence: float | None = None


@router.post("/voice_stt", response_model=STTResponse)
async def voice_stt(file: UploadFile = File(...)):
    """
    Convert speech → text using Whisper
    """

    # Check if file exists
    if not file:
        raise HTTPException(status_code=400, detail="No audio file provided")

    # Read bytes
    content = await file.read()
    size = len(content)

    # Check size
    if size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max allowed = {MAX_FILE_SIZE / (1024 * 1024)} MB"
        )

    # Check mimetype
    if file.content_type not in SUPPORTED_MIMETYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Supported: {', '.join(SUPPORTED_MIMETYPES)}"
        )

    # Save temporary file
    extension = SUPPORTED_MIMETYPES[file.content_type]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    model = load_whisper_model()

    try:
        logger.info("Transcribing audio...")
        result = model.transcribe(tmp_path)
        logger.info("Transcription done.")

        text = result.get("text", "").strip()
        language = result.get("language", "unknown")

        # Estimate confidence score (not provided natively)
        confidence = None
        if "segments" in result and result["segments"]:
            scores = [seg.get("avg_logprob", 0) for seg in result["segments"]]
            if scores:
                avg = sum(scores) / len(scores)
                confidence = 1 / (1 + (-avg))  # sigmoid approximation

        return STTResponse(text=text, language=language, confidence=confidence)

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"STT Processing failed: {e}")

    finally:
        try:
            os.unlink(tmp_path)
        except:
            pass
