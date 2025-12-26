from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

class ResponseComposer:
    """
    Response Composer Module
    Produces deterministic assistant output blocks based on inputs.
    """

    def __init__(self):
        self.templates = {
            "task_created": {
                "message_template": "I've created a {task_type} task for you: {description}.",
                "action_template": "Created {task_type} task with priority {priority}.",
                "next_steps": ["Review task details", "Modify if needed"]
            },
            "task_scheduled": {
                "message_template": "I've scheduled your {task_type} for {datetime}.",
                "action_template": "Scheduled {task_type} at {datetime}.",
                "next_steps": ["Check calendar", "Set reminder"]
            },
            "task_deferred": {
                "message_template": "I've noted that down but haven't scheduled it yet.",
                "action_template": "Deferred task creation.",
                "next_steps": ["Provide time to schedule", "Add more details"]
            },
            "task_failed": {
                "message_template": "I encountered an issue while processing your request.",
                "action_template": "Failed to execute task: {error_reason}.",
                "next_steps": ["Retry with clear instructions", "Check system status"]
            },
            "clarification_needed": {
                "message_template": "I need a bit more information to proceed. {clarification_prompt}",
                "action_template": "Requested clarification.",
                "next_steps": ["Provide missing details"]
            },
            "default": {
                "message_template": "{response_text}",
                "action_template": "Processed request.",
                "next_steps": []
            }
        }

    def compose_response(
        self,
        summary: Dict[str, Any] = None,
        task: Dict[str, Any] = None,
        routing: Dict[str, Any] = None,
        execution_status: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Composes a deterministic response based on the provided inputs.
        
        Args:
            summary: Output from SummaryFlow
            task: Output from TaskFlow
            routing: Output from DecisionHub/Router
            execution_status: Status of the execution (e.g., success, error)
            
        Returns:
            Dict containing assistant_message, action_taken, next_steps, confidence_level, trace_id
        """
        summary = summary or {}
        task = task or {}
        routing = routing or {}
        execution_status = execution_status or {"status": "success"}

        # Determine the scenario
        scenario = self._determine_scenario(task, execution_status, routing)
        template = self.templates.get(scenario, self.templates["default"])

        # Prepare context for templates
        context = self._prepare_context(summary, task, routing, execution_status)

        # Generate fields
        assistant_message = template["message_template"].format(**context)
        action_taken = template["action_template"].format(**context)
        next_steps = template["next_steps"]
        
        # Calculate confidence
        confidence_level = self._calculate_confidence(task, routing)
        
        # Trace ID
        trace_id = execution_status.get("trace_id", str(uuid.uuid4()))

        return {
            "assistant_message": assistant_message,
            "action_taken": action_taken,
            "next_steps": next_steps,
            "confidence_level": confidence_level,
            "trace_id": trace_id
        }

    def _determine_scenario(self, task: Dict, execution_status: Dict, routing: Dict) -> str:
        status = execution_status.get("status")
        
        if status == "error":
            return "task_failed"
        
        if status == "clarification_needed":
            return "clarification_needed"
            
        if execution_status.get("deferred", False):
            return "task_deferred"

        if task and task.get("task_type"):
            task_type = task.get("task_type")
            # Check if it has a specific schedule
            params = task.get("parameters", {})
            if params.get("datetime"):
                return "task_scheduled"
            return "task_created"
        
        # Fallback to default response handling
        return "default"

    def _prepare_context(self, summary: Dict, task: Dict, routing: Dict, execution_status: Dict) -> Dict:
        """
        Flattens and prepares context for string formatting.
        Handles missing keys gracefully.
        """
        context = {
            "task_type": "task",
            "description": "item",
            "priority": "normal",
            "datetime": "unspecified time",
            "error_reason": "unknown error",
            "clarification_prompt": "Could you provide more details?",
            "response_text": "I processed your request."
        }

        # Update with task info
        if task:
            context["task_type"] = task.get("task_type", "task")
            context["priority"] = task.get("priority", "normal")
            params = task.get("parameters", {})
            context["description"] = params.get("message") or params.get("query") or "item"
            context["datetime"] = params.get("datetime", "unspecified time")

        # Update with execution status
        if execution_status:
            context["error_reason"] = execution_status.get("error", "unknown error")
            context["clarification_prompt"] = execution_status.get("clarification_prompt", "Could you provide more details?")

        # Update with routing/response info for default case
        if routing:
            # If routing has a direct response (e.g. from LLM)
            context["response_text"] = routing.get("response") or routing.get("processed_text") or "I processed your request."
            
        return context

    def _calculate_confidence(self, task: Dict, routing: Dict) -> str:
        """
        Returns high/medium/low based on numeric confidence.
        """
        # Try to get confidence from task or routing
        conf_val = task.get("confidence") or routing.get("confidence") or 1.0
        
        try:
            val = float(conf_val)
            if val >= 0.8:
                return "high"
            elif val >= 0.5:
                return "medium"
            else:
                return "low"
        except (ValueError, TypeError):
            return "medium"

# Global instance
response_composer = ResponseComposer()
