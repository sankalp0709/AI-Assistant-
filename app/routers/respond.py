from fastapi import APIRouter
from pydantic import BaseModel
from ..core.llm_bridge import llm_bridge

router = APIRouter()

class RespondRequest(BaseModel):
    query: str
    context: dict = {}
    model: str = "uniguru"

@router.post("/respond")
async def generate_response(request: RespondRequest):
    prompt = f"Context: {request.context}\nQuery: {request.query}\nProvide a helpful response."
    response = await llm_bridge.call_llm(request.model, prompt)
    return {"response": response}
