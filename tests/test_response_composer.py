import sys
import os

# Insert parent dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.response_composer import response_composer

def test_missing_task():
    result = response_composer.compose_response(
        summary={"summary": "Buy milk"},
        task={},
        routing={},
        execution_status={"status": "success"}
    )
    assert "assistant_message" in result
    assert "action_taken" in result
    assert "next_steps" in result
    assert "confidence_level" in result
    assert "trace_id" in result
    assert result["response_version"] == "v1"

def test_missing_execution_status():
    result = response_composer.compose_response(
        summary={},
        task={"task_type": "reminder", "parameters": {"message": "buy milk"}, "priority": "normal"},
        routing={},
        execution_status=None
    )
    assert result["confidence_level"] in ["high", "medium", "low"]
    assert result["response_version"] == "v1"

def test_only_routing():
    result = response_composer.compose_response(
        summary={},
        task={},
        routing={"response": "Hello"},
        execution_status={"status": "success"}
    )
    assert result["assistant_message"] == "I processed your request."
    assert result["response_version"] == "v1"

def test_confidence_numeric_only():
    result = response_composer.compose_response(
        summary={},
        task={},
        routing={"confidence": 0.6},
        execution_status={"status": "success"}
    )
    assert result["confidence_level"] == "medium"
    assert result["response_version"] == "v1"

def test_clarification_mode_trigger():
    result = response_composer.compose_response(
        summary={},
        task={},
        routing={},
        execution_status={"status": "clarification_needed", "clarification_prompt": "Specify date"}
    )
    assert "I need a bit more information" in result["assistant_message"]
    assert result["response_version"] == "v1"
