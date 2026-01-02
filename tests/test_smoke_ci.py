import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.response_composer import response_composer

def test_arl_smoke_contract():
    routing = {"final_decision": "response_generated", "intent": "general", "confidence": 0.9}
    task = {"task_type": "note", "parameters": {"message": "Smoke test"}}
    execution_status = {"status": "success", "trust": {"confidence_verified": True, "confidence": 0.85}}
    data = response_composer.compose_response(routing=routing, task=task, execution_status=execution_status)
    required = ["assistant_message", "action_taken", "next_steps", "confidence_level", "trace_id", "response_version"]
    for k in required:
        assert k in data
    assert data["response_version"] == "v1"
