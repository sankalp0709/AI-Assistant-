from fastapi import APIRouter
from pydantic import BaseModel
from ..core.llm_bridge import llm_bridge

router = APIRouter()

class IntentRequest(BaseModel):
    text: str
    model: str = "uniguru"

@router.post("/intent")
async def detect_intent(request: IntentRequest):
    prompt = f"""Analyze the following text and classify its intent into one of these categories:
- task: if the user wants to create, manage, or track a task/todo item
- summarize: if the user wants a summary of content
- general: for general questions, statements, or other intents

Text: {request.text}

Return only the intent category (task, summarize, or general):"""
    intent = await llm_bridge.call_llm(request.model, prompt)
    intent = intent.strip().lower()

    # Normalize the response
    if "task" in intent:
        return {"intent": "task"}
    elif "summarize" in intent or "summary" in intent:
        return {"intent": "summarize"}
    else:
        return {"intent": "general"}
