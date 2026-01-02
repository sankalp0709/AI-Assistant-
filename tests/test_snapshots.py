import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app.core.response_composer import response_composer

def load_cases():
    path = os.path.join(os.path.dirname(__file__), "snapshot_cases.json")
    with open(path, "r") as f:
        return json.load(f)

@pytest.mark.parametrize("case", load_cases())
def test_snapshot(case):
    inputs = case["input"]
    result = response_composer.compose_response(
        summary=inputs.get("summary"),
        task=inputs.get("task"),
        routing=inputs.get("routing"),
        execution_status=inputs.get("execution_status")
    )
    expected = case["expected"]
    assert result == expected
