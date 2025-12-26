# Assistant Response Layer (ARL)

## Overview
The **Assistant Response Layer (ARL)** is the final output formatting stage of the AI Assistant. Its purpose is to transform internal system states (tasks, routing decisions, execution status) into **deterministic, human-readable, and frontend-friendly** JSON responses.

This layer ensures that regardless of the complex logic happening inside the BHIV core (multi-agent reasoning, task flows), the client always receives a structured response that is easy to render.

## Input → Output Flow

### Input
The Response Composer takes four key inputs:
1. **Summary** (from SummaryFlow): Structured summary of user intent.
2. **Task** (from TaskFlow): Structured task object (if created).
3. **Routing** (from DecisionHub): Logic about which agent/LLM handled the request.
4. **Execution Status**: Success/failure flags and error messages.

### Output Example
```json
{
  "assistant_message": "I've scheduled your meeting for 2023-10-27T10:00:00.",
  "action_taken": "Scheduled meeting at 2023-10-27T10:00:00.",
  "next_steps": [
    "Check calendar",
    "Set reminder"
  ],
  "confidence_level": "high",
  "trace_id": "db9f789a-e145-46c2-a087-3534d907a770"
}
```

## Frontend Consumption Guide

Frontend clients (Web, Mobile, Desktop) should consume the response as follows:

| Field | Purpose | Rendering Recommendation |
|-------|---------|--------------------------|
| `assistant_message` | The primary response to the user. | Display in a chat bubble (left/agent side). |
| `action_taken` | A concise system log of what happened. | Display in a small "status" or "debug" footer/toast. |
| `next_steps` | Suggested follow-up actions. | Render as clickable chips or buttons below the message. |
| `confidence_level` | System confidence (high/medium/low). | Optional: Show an indicator if confidence is "low". |
| `trace_id` | Unique ID for the request. | Log this internally for debugging; do not show to user. |

## Templates & Scenarios

The system currently supports the following deterministic scenarios:

1. **Task Created**: When a task is created but not scheduled (no specific time).
2. **Task Scheduled**: When a task has a specific `datetime`.
3. **Task Deferred**: When a task is recognized but explicitly deferred.
4. **Task Failed**: When an error occurs during execution.
5. **Clarification Needed**: When the system needs more info.
6. **Default**: Standard chat response.

## ⚠️ What Not To Change

1. **Field Names**: Do not change `assistant_message`, `action_taken`, or `next_steps`. The frontend relies on these exact keys.
2. **Deterministic Logic**: Do not replace the template-based generation with an LLM call. This layer MUST be deterministic to ensure reliability and speed.
3. **Trace ID**: Always ensure a `trace_id` is passed or generated for observability.

## Adding New Templates

To add a new scenario:
1. Open `app/core/response_composer.py`.
2. Add a new key to `self.templates` in `__init__`.
3. Update `_determine_scenario` logic to detect when to use this new template.
4. Add a test case in `tests/test_response_composer.py`.
