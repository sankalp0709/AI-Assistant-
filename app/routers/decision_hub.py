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

    try:
        decision = await decision_hub.make_decision(
            input_text,
            platform,
            device_context,
            voice_input,
            audio_data
        )
        
        execution_status = {"status": "success"}
        if "integration_error" in decision:
            execution_status = {
                "status": "error",
                "error": decision["integration_error"]
            }

        if decision.get("final_decision") == "bhiv_core":
            try:
                class BHIVInput:
                    def __init__(self, query, context):
                        self.query = query
                        self.context = context
                
                bhiv_input = BHIVInput(
                    query=decision.get("processed_text", input_text),
                    context={"intent": decision.get("intent")}
                )
                
                bhiv_result = await bhiv.process(bhiv_input)
                decision["bhiv_output"] = bhiv_result
                if isinstance(bhiv_result, dict):
                     decision["response"] = bhiv_result.get("response") or str(bhiv_result)
                else:
                     decision["response"] = str(bhiv_result)
                     
            except Exception as e:
                execution_status = {"status": "error", "error": f"BHIV execution failed: {str(e)}"}

        formatted_response = response_composer.compose_response(
            routing=decision,
            task=decision.get("task_created") or decision.get("task_data"),
            execution_status=execution_status
        )
        return formatted_response
    except Exception as e:
        return response_composer.compose_response(
            routing={},
            task={},
            execution_status={"status": "error", "error": str(e)}
        )
