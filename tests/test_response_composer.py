import sys
import os
import json
import uuid

# Add app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.response_composer import response_composer

def run_tests():
    print("Running Response Composer Tests...\n")
    
    test_cases = [
        {
            "name": "Task Created (Reminder)",
            "input": {
                "summary": {"summary": "User wants to buy milk."},
                "task": {
                    "task_type": "reminder",
                    "parameters": {"message": "buy milk"},
                    "priority": "normal",
                    "confidence": 0.9
                },
                "routing": {},
                "execution_status": {"status": "success"}
            },
            "expected_scenario": "task_created"
        },
        {
            "name": "Task Scheduled (Meeting)",
            "input": {
                "summary": {"summary": "Meeting with Bob tomorrow."},
                "task": {
                    "task_type": "meeting",
                    "parameters": {"message": "Meeting with Bob", "datetime": "2023-10-27T10:00:00"},
                    "priority": "high",
                    "confidence": 0.85
                },
                "routing": {},
                "execution_status": {"status": "success"}
            },
            "expected_scenario": "task_scheduled"
        },
        {
            "name": "Task Deferred",
            "input": {
                "summary": {"summary": "User mentioned reading a book sometime."},
                "task": {},
                "routing": {},
                "execution_status": {"status": "success", "deferred": True}
            },
            "expected_scenario": "task_deferred"
        },
        {
            "name": "Task Failed",
            "input": {
                "summary": {"summary": "Complex impossible task."},
                "task": {"task_type": "general"},
                "routing": {},
                "execution_status": {"status": "error", "error": "Database connection failed"}
            },
            "expected_scenario": "task_failed"
        },
        {
            "name": "Clarification Needed",
            "input": {
                "summary": {"summary": "User said 'do it'."},
                "task": {},
                "routing": {},
                "execution_status": {"status": "clarification_needed", "clarification_prompt": "What would you like me to do?"}
            },
            "expected_scenario": "clarification_needed"
        },
        {
            "name": "Default Response (Q&A)",
            "input": {
                "summary": {"summary": "User asked about weather."},
                "task": {},
                "routing": {"response": "The weather is sunny today.", "confidence": 0.95},
                "execution_status": {"status": "success"}
            },
            "expected_scenario": "default"
        }
    ]

    for case in test_cases:
        print(f"--- Test Case: {case['name']} ---")
        try:
            result = response_composer.compose_response(**case['input'])
            print(json.dumps(result, indent=2))
            
            # Basic validation
            assert "assistant_message" in result
            assert "action_taken" in result
            assert "next_steps" in result
            assert "confidence_level" in result
            assert "trace_id" in result
            
            # Check specific fields based on expected scenario (simplified check)
            if case['expected_scenario'] == "task_failed":
                assert "Failed" in result["action_taken"]
            elif case['expected_scenario'] == "clarification_needed":
                assert "clarification" in result["action_taken"]
                
            print("✅ PASSED\n")
        except Exception as e:
            print(f"❌ FAILED: {str(e)}\n")

if __name__ == "__main__":
    run_tests()
