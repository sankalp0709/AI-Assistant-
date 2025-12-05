# TODO: Integrate with Chandresh's EmbedCore v3 module once completed
# Current implementation uses sentence-transformers directly
# Future: Replace with EmbedCore v3 for enhanced embedding capabilities

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import hashlib

router = APIRouter()

# Global model and cache
model = None
cache = {}

def load_model():
    global model
    if model is None:
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")


class EmbedRequest(BaseModel):
    texts: List[str]


class SimilarityRequest(BaseModel):
    texts1: List[str]
    texts2: List[str]


@router.post("/embed")
async def generate_embeddings(request: EmbedRequest):
    if not request.texts:
        return {"embeddings": []}

    if model is None:
        load_model()

    embeddings = []
    for text in request.texts:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in cache:
            embedding = cache[text_hash]
        else:
            try:
                embedding = model.encode(text).tolist()
                cache[text_hash] = embedding
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Embedding computation failed: {e}")

        embeddings.append(embedding)

    return {"embeddings": embeddings}


@router.post("/embed/similarity")
async def compute_similarity(request: SimilarityRequest):
    if not request.texts1 or not request.texts2:
        return {"similarities": []}

    if model is None:
        load_model()

    # Get embeddings for texts1
    emb1 = []
    for text in request.texts1:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in cache:
            emb = cache[text_hash]
        else:
            try:
                emb = model.encode(text).tolist()
                cache[text_hash] = emb
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Embedding computation failed: {e}")
        emb1.append(emb)

    # Get embeddings for texts2
    emb2 = []
    for text in request.texts2:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in cache:
            emb = cache[text_hash]
        else:
            try:
                emb = model.encode(text).tolist()
                cache[text_hash] = emb
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Embedding computation failed: {e}")
        emb2.append(emb)

    # Compute pairwise cosine similarities
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity(emb1, emb2).tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similarity computation failed: {e}")

    return {"similarities": similarities}
