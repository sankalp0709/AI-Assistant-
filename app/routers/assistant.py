from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..core.summaryflow import summary_flow
from ..core.intentflow import intent_flow
from ..core.taskflow import task_flow
from ..core.decision_hub import decision_hub

router = APIRouter()

class AssistantRequest(BaseModel):
    message: Optional[str] = None  # Raw user message
    summarized_payload: Optional[Dict[str, Any]] = None  # Alternative input
    platform: str = "web"
    device_context: str = "desktop"
    voice_input: bool = False

class AssistantResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    error: Optional[str] = None

@router.post("/assistant", response_model=AssistantResponse)
async def process_assistant_request(request: AssistantRequest):
    try:
        # Determine input text for processing
        if request.message:
            input_text = request.message
        elif request.summarized_payload and "summary" in request.summarized_payload:
            input_text = request.summarized_payload["summary"]
        else:
            return AssistantResponse(
                status="error",
                data={},
                error="Invalid input: Either message or summarized_payload with summary field must be provided"
            )

        # Step 1: SummaryFlow - Generate summary if raw message provided
        try:
            if request.message:
                summary = summary_flow.generate_summary(request.message)
            else:
                summary = request.summarized_payload
        except Exception as e:
            return AssistantResponse(
                status="error",
                data={},
                error="Summary processing failed"
            )

        # Step 2: ContextFlow (Task Creation) - Intent detection and task building
        try:
            intent_data = intent_flow.process_text(input_text)
        except Exception as e:
            return AssistantResponse(
                status="error",
                data={},
                error="Intent detection failed"
            )

        try:
            task_data = task_flow.build_task(intent_data)
        except Exception as e:
            return AssistantResponse(
                status="error",
                data={},
                error="Task creation failed"
            )

        # Step 3: Decision Hub - Make decision with routing
        try:
            decision = await decision_hub.make_decision(
                input_text=input_text,
                platform=request.platform,
                device_context=request.device_context,
                voice_input=request.voice_input
            )
        except Exception as e:
            return AssistantResponse(
                status="error",
                data={},
                error="Decision processing failed"
            )

        # Step 4: Routing - Decision Hub already handles routing internally

        # Prepare clean response envelope for Sankalp
        response_data = {
            "summary": summary,
            "intent": intent_data,
            "task": task_data,
            "decision": decision,
            "processed_at": intent_data.get("timestamp")
        }

        return AssistantResponse(
            status="success",
            data=response_data
        )

    except Exception as e:
        return AssistantResponse(
            status="error",
            data={},
            error="Internal processing error"
        )