from fastapi import APIRouter
from pydantic import BaseModel
from ..core.system import bhiv

router = APIRouter()

class BHIVRequest(BaseModel):
    query: str
    context: dict = {}

@router.post("/bhiv/run")
async def run_bhiv(request: BHIVRequest):
    result = await bhiv.process(request)
    return {"bhiv_output": result}