from fastapi import APIRouter
from pydantic import BaseModel
from ..core.llm_bridge import llm_bridge
from ..core.system import bhiv

router = APIRouter()

class RespondRequest(BaseModel):
    query: str
    context: dict = {}
    model: str = "uniguru"
    decision: str = "respond"

@router.post("/respond")
async def generate_response(request: RespondRequest):
    try:
        if request.decision == "bhiv_core":
            return await bhiv.process(request)
        prompt = f"Context: {request.context}\nQuery: {request.query}\nProvide a helpful response."
        response = await llm_bridge.call_llm(request.model, prompt)
        return {"response": response}
    except Exception as e:
        return {"error": f"Failed to generate response: {str(e)}"}
