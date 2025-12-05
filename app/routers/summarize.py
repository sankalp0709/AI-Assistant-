from fastapi import APIRouter
from pydantic import BaseModel
from ..core.llm_bridge import llm_bridge

router = APIRouter()

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 100
    model: str = "uniguru"

@router.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    prompt = f"Summarize the following text in {request.max_length} words or less:\n{request.text}"
    summary = await llm_bridge.call_llm(request.model, prompt)
    return {"summary": summary}
