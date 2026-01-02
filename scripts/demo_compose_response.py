import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.response_composer import response_composer

def demo():
    cases = [
        {"name": "Missing task", "payload": {"summary": {"summary": "Buy milk"}, "task": {}, "routing": {}, "execution_status": {"status": "success"}}},
        {"name": "Missing execution_status", "payload": {"summary": {}, "task": {"task_type": "reminder", "parameters": {"message": "buy milk"}, "priority": "normal"}, "routing": {}, "execution_status": None}},
        {"name": "Only routing", "payload": {"summary": {}, "task": {}, "routing": {"response": "Hello", "confidence": 0.9}, "execution_status": {"status": "success"}}},
        {"name": "Confidence numeric only", "payload": {"summary": {}, "task": {}, "routing": {"confidence": 0.6}, "execution_status": {"status": "success"}}},
        {"name": "Clarification mode", "payload": {"summary": {}, "task": {}, "routing": {}, "execution_status": {"status": "clarification_needed", "clarification_prompt": "Specify date"}}},
    ]
    for c in cases:
        result = response_composer.compose_response(**c["payload"])
        print(json.dumps({"case": c["name"], "result": result}, indent=2))

if __name__ == "__main__":
    demo()
