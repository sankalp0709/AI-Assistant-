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
        # Safe default initialization
        summary = summary or {}
        task = task or {}
        routing = routing or {}
        execution_status = execution_status or {"status": "success"}

        # trust readiness inputs
        trust_block = {}
        if isinstance(routing, dict) and isinstance(routing.get("trust"), dict):
            trust_block = routing.get("trust") or {}
        elif isinstance(execution_status, dict) and isinstance(execution_status.get("trust"), dict):
            trust_block = execution_status.get("trust") or {}
        verified_conf = None
        try:
            if trust_block.get("confidence_verified") is True:
                verified_conf = trust_block.get("confidence")
            elif routing.get("confidence_verified") is True:
                verified_conf = routing.get("verified_confidence")
            elif execution_status.get("confidence_verified") is True:
                verified_conf = execution_status.get("verified_confidence")
        except Exception:
            verified_conf = None
        verified_trace = None
        try:
            if trust_block.get("trace_ref_verified") is True:
                verified_trace = trust_block.get("trace_ref")
            elif isinstance(routing.get("verified_trace_id"), str):
                verified_trace = routing.get("verified_trace_id")
            elif isinstance(execution_status.get("verified_trace_id"), str):
                verified_trace = execution_status.get("verified_trace_id")
        except Exception:
            verified_trace = None
        _auth_tag = trust_block.get("authenticity_tag") or routing.get("authenticity_tag") or execution_status.get("authenticity_tag")

        # trace_id consistency: Look in all inputs safely, prefer verified
        try:
            trace_id = (
                (isinstance(verified_trace, str) and verified_trace) or
                (isinstance(execution_status, dict) and execution_status.get("trace_id")) or 
                (isinstance(task, dict) and task.get("trace_id")) or 
                (isinstance(summary, dict) and summary.get("trace_id")) or 
                (isinstance(routing, dict) and routing.get("trace_id")) or 
                str(uuid.uuid4())
            )
        except Exception:
            trace_id = str(uuid.uuid4())

        try:
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
            confidence_level = self._calculate_confidence(task, routing, verified_conf)
            
            return self._validate_output({
                "assistant_message": assistant_message,
                "action_taken": action_taken,
                "next_steps": next_steps,
                "confidence_level": confidence_level,
                "trace_id": trace_id,
                "response_version": "v1"
            })
            
        except Exception as e:
            # Fallback for unexpected failures
            return self._validate_output({
                "assistant_message": "I encountered an internal error while processing your request.",
                "action_taken": "System error caught during response composition.",
                "next_steps": ["Retry request", "Contact support"],
                "confidence_level": "low",
                "trace_id": trace_id,
                "response_version": "v1"
            })

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

        # Use summary as a graceful fallback for description
        if summary and context["description"] == "item":
            context["description"] = summary.get("summary") or "item"

        # Update with execution status
        if execution_status:
            context["error_reason"] = execution_status.get("error", "unknown error")
            context["clarification_prompt"] = execution_status.get("clarification_prompt", "Could you provide more details?")

        if routing:
            context["response_text"] = "I processed your request."
            
        return context

    def _calculate_confidence(self, task: Dict, routing: Dict, override: Optional[float] = None) -> str:
        """
        Returns high/medium/low based on numeric confidence.
        """
        # Try to get confidence from override, task or routing
        conf_val = override if override is not None else (task.get("confidence") or routing.get("confidence") or 1.0)
        
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
    
    def _validate_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        msg = data.get("assistant_message")
        data["assistant_message"] = msg if isinstance(msg, str) and msg.strip() else "I processed your request."
        act = data.get("action_taken")
        data["action_taken"] = act if isinstance(act, str) and act.strip() else "Processed request."
        steps = data.get("next_steps", [])
        data["next_steps"] = steps if isinstance(steps, list) else []
        conf = data.get("confidence_level", "medium")
        data["confidence_level"] = conf if conf in ["high", "medium", "low"] else "medium"
        tid = data.get("trace_id")
        data["trace_id"] = tid if isinstance(tid, str) and tid else str(uuid.uuid4())
        # Freeze contract version: always v1
        data["response_version"] = "v1"
        return data

# Global instance
response_composer = ResponseComposer()
