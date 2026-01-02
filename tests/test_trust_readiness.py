import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.response_composer import response_composer

def test_verified_confidence_mapping():
    routing = {"trust": {"confidence": 0.9, "confidence_verified": True}}
    result = response_composer.compose_response(summary={}, task={}, routing=routing, execution_status={"status": "success"})
    assert result["confidence_level"] == "high"
    assert "response_version" in result

def test_verified_trace_passthrough():
    execution_status = {"status": "success", "trust": {"trace_ref": "trusted-abc", "trace_ref_verified": True}}
    result = response_composer.compose_response(summary={}, task={}, routing={}, execution_status=execution_status)
    assert result["trace_id"] == "trusted-abc"
    assert "response_version" in result
