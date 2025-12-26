from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from ..core.system import decision_hub, bhiv
from ..core.response_composer import response_composer

router = APIRouter()

class DecisionRequest(BaseModel):
    input_text: str
    platform: str = "web"
    device_context: str = "desktop"
    voice_input: bool = False

@router.post("/decision_hub")
async def make_decision(
    input_text: str = Form(...),
    platform: str = Form("web"),
    device_context: str = Form("desktop"),
    voice_input: bool = Form(False),
    audio_file: Optional[UploadFile] = File(None)
):
    audio_data = None
    if audio_file:
        audio_data = await audio_file.read()

    decision = await decision_hub.make_decision(
        input_text,
        platform,
        device_context,
        voice_input,
        audio_data
    )
    
    # Execution Status
    execution_status = {"status": "success"}
    if "integration_error" in decision:
        execution_status = {
            "status": "error",
            "error": decision["integration_error"]
        }

    # Handle BHIV Core routing
    if decision.get("final_decision") == "bhiv_core":
        try:
            # We need to construct a request object that BHIV expects.
            # Assuming BHIV expects an object with .query and .context attributes or dict.
            # bhiv.process(request) expects an object with .query attribute based on RespondRequest in respond.py
            # But in bhiv.py it uses BHIVRequest which has query and context.
            # Let's create a simple object or dict.
            
            class BHIVInput:
                def __init__(self, query, context):
                    self.query = query
                    self.context = context
            
            bhiv_input = BHIVInput(
                query=decision.get("processed_text", input_text),
                context={"intent": decision.get("intent")}
            )
            
            bhiv_result = await bhiv.process(bhiv_input)
            
            # Update decision with BHIV result
            decision["bhiv_output"] = bhiv_result
            # Assuming BHIV returns a text response in the result, or we need to extract it.
            # If bhiv_result is a string, use it. If dict, extract.
            if isinstance(bhiv_result, dict):
                 decision["response"] = bhiv_result.get("response") or str(bhiv_result)
            else:
                 decision["response"] = str(bhiv_result)
                 
        except Exception as e:
            execution_status = {"status": "error", "error": f"BHIV execution failed: {str(e)}"}

    # Compose standardized response
    formatted_response = response_composer.compose_response(
        routing=decision,
        task=decision.get("task_created") or decision.get("task_data"),
        execution_status=execution_status
    )

    return formatted_response
