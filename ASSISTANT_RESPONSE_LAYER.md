# Assistant Response Layer

## Purpose
- Structures assistant outputs after Decision Hub logic and before UI rendering.
- Ensures clarity, determinism, and usability without changing upstream/downstream schemas.
- Provides fixed, human-readable blocks consumed by frontend and backend glue.

## Input
- A single JSON payload:
```
{
  "summary": { ... },
  "task": { ... },
  "routing": { ... },
  "execution_status": { ... }
}
```

## Output
- Deterministic assistant blocks:
```
{
  "assistant_message": "...",
  "action_taken": "...",
  "next_steps": [ "...", "..." ],
  "confidence_level": "...",
  "trace_id": "..."
}
```

## Module
- File: `src/response_composer.js`
- Export: `composeAssistantResponse(payload)`
- Behavior:
  - Maps decision payload to fixed templates: created, scheduled, deferred, failed, clarification_needed.
  - Derives `confidence_level` from `execution_status.confidence_level` or `summary.confidence_level`, or maps numeric confidence.
  - Resolves `trace_id` from `routing.trace_id` or `execution_status.trace_id` or `task.id`; falls back to a deterministic hash of the payload.
  - Produces plain language with no free-form text, no emojis, and no system leakage.

## Templates
- Created
  - `assistant_message`: "Task created." + optional task name
  - `action_taken`: "Created task"
  - `next_steps`: ["Begin execution", "Monitor progress"]
  - `confidence_level`: derived
  - `trace_id`: resolved
- Scheduled
  - `assistant_message`: "Task scheduled." + optional task name
  - `action_taken`: "Scheduled task"
  - `next_steps`: ["Await schedule", "Confirm start"]
  - `confidence_level`: derived
  - `trace_id`: resolved
- Deferred
  - `assistant_message`: "Task deferred." + optional task name
  - `action_taken`: "Deferred task"
  - `next_steps`: ["Resolve blockers", "Reschedule"]
  - `confidence_level`: derived
  - `trace_id`: resolved
- Failed
  - `assistant_message`: "Task failed." + optional task name
  - `action_taken`: "Recorded failure"
  - `next_steps`: ["Review cause", "Apply fix", "Retry"]
  - `confidence_level`: derived
  - `trace_id`: resolved
- Clarification Needed
  - `assistant_message`: "Clarification needed." + optional task name
  - `action_taken`: "Requested clarification"
  - `next_steps`: ["Provide missing details", "Confirm scope"]
  - `confidence_level`: derived
  - `trace_id`: resolved

## Consumption
- Frontend (Yash)
  - Render `assistant_message` prominently.
  - Display `action_taken` as the status label.
  - Show `next_steps` as a checklist or instruction list.
  - Use `confidence_level` for visual indicators (e.g., badge).
  - Use `trace_id` for tracing and linking across views.
- Backend glue (Nilesh)
  - Pass Decision Hub payload directly to `composeAssistantResponse`.
  - Persist only the returned block; do not modify.
  - Avoid adding fields; the output is complete for UI use.

## Input → Output Example
- Input file: `examples/payload_task_scheduled.json`
- Output file: `examples/output_task_scheduled.json`
```
Input
{
  "summary": { "title": "Database backup", "confidence": 0.72 },
  "task": { "id": "T-002", "title": "Nightly DB Backup", "status": "scheduled" },
  "routing": { "trace_id": "trace-002", "path": "ops.backup" },
  "execution_status": { "status": "scheduled" }
}

Output
{
  "assistant_message": "Task scheduled. Nightly DB Backup.",
  "action_taken": "Scheduled task",
  "next_steps": ["Await schedule", "Confirm start"],
  "confidence_level": "high",
  "trace_id": "trace-002"
}
```

## Testing
- Sample payloads and expected outputs are under `examples/`.
- Determinism: same input yields the same output.
- No ambiguity: all fields are present and stable.

## What Not To Change
- Do not change input payload schema.
- Do not add or remove output fields.
- Do not introduce new APIs, routing, auth, or storage integrations.
- Do not inject system internals into messages.

## Handover
- Files:
  - `src/response_composer.js`
  - `examples/` (payload and output pairs)
  - `ASSISTANT_RESPONSE_LAYER.md`
- Status: Ready for frontend + backend consumption
