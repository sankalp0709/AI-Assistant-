import sys
import os
import json
import uuid

# Add app to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.response_composer import ResponseComposer

def generate_examples():
    composer = ResponseComposer()
    
    # Example 1: Task Scheduled
    print("--- Example 1: Task Scheduled ---")
    routing_1 = {"intent": "schedule_meeting"}
    task_1 = {
        "task_type": "meeting",
        "parameters": {"datetime": "2025-10-27T10:00:00", "description": "Strategy Sync"}
    }
    status_1 = {"status": "success"}
    
    response_1 = composer.compose_response(routing=routing_1, task=task_1, execution_status=status_1)
    print(json.dumps(response_1, indent=2))
    
    # Example 2: Clarification Needed
    print("\n--- Example 2: Clarification Needed ---")
    routing_2 = {"intent": "unknown"}
    task_2 = None
    status_2 = {"status": "clarification_needed", "clarification_prompt": "Could you specify the duration?"}
    
    response_2 = composer.compose_response(routing=routing_2, task=task_2, execution_status=status_2)
    print(json.dumps(response_2, indent=2))
    
    # Example 3: Task Failed
    print("\n--- Example 3: Task Failed ---")
    routing_3 = {"intent": "create_file"}
    task_3 = {"task_type": "file_op"}
    status_3 = {"status": "error", "error": "Permission denied"}
    
    response_3 = composer.compose_response(routing=routing_3, task=task_3, execution_status=status_3)
    print(json.dumps(response_3, indent=2))

if __name__ == "__main__":
    generate_examples()
