import json
import pytest
import sys
import os

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.response_composer import response_composer

def load_regression_data():
    data_path = os.path.join(os.path.dirname(__file__), 'regression_data.json')
    with open(data_path, 'r') as f:
        return json.load(f)

@pytest.mark.parametrize("case", load_regression_data())
def test_regression_case(case):
    """
    Runs regression tests from data pack.
    """
    print(f"Running test case: {case['name']}")
    
    # Extract inputs
    inputs = case["input"]
    
    # Run composer
    result = response_composer.compose_response(
        summary=inputs.get("summary"),
        task=inputs.get("task"),
        routing=inputs.get("routing"),
        execution_status=inputs.get("execution_status")
    )
    
    # Validate expected partial matches
    expected = case["expected_partial"]
    for key, val in expected.items():
        assert result.get(key) == val, f"Mismatch in {key} for case '{case['name']}'. Expected '{val}', got '{result.get(key)}'"
    
    # Validate mandatory contract fields
    mandatory_fields = [
        "assistant_message", "action_taken", "next_steps", 
        "confidence_level", "trace_id", "response_version"
    ]
    for field in mandatory_fields:
        assert field in result, f"Missing mandatory field {field} in case '{case['name']}'"
        
    # Validate version
    assert result["response_version"] == "v1"

if __name__ == "__main__":
    # Allow running directly
    pytest.main([__file__])
