# Assistant Response Contract — v1

## Version
- Contract Version: v1
- Status: Frozen (immutable); changes require a new version (v2, v3, …)

## Purpose
- Define the final, deterministic response payload returned by the Assistant Response Layer (ARL)
- Ensure UI and backend consumers have a stable, versioned contract

## Required Fields
- assistant_message: string (non-empty after validation)
- action_taken: string (non-empty after validation)
- next_steps: array<string>
- confidence_level: enum ["high", "medium", "low"]
- trace_id: string
- response_version: "v1"

## Optional Fields
- None (closed contract for determinism and stability)

## Never Allowed Fields
- Upstream internals from summary/intent/task/decision flows:
  - Summary internals: key_points, entities, word_count, sentence_count, timestamp, version
  - Intent internals: entities, dates_times, context, confidence, timestamp, version, original_text
  - Task internals: parameters, priority, confidence, timestamp, version
  - Decision internals: confidence, selected_agent, preferred_llm, device_context, memory_reference, intent, processed_text, voice_output
- LLM/Agent metadata:
  - Provider/model names, prompts, temperatures, top-p, stop sequences, tokens
  - Agent names, intermediate steps, tool parameters
- Debug/server details:
  - Stack traces, environment variables, logs, Sentry IDs, file paths, DB references

## Determinism Guarantee
- ARL produces responses via fixed templates only; no free-form LLM generation in ARL
- Types and enums are validated with safe fallbacks in code:
  - assistant_message: string → fallback "I processed your request."
  - action_taken: string → fallback "Processed request."
  - next_steps: array<string> → fallback []
  - confidence_level: enum → fallback "medium"
  - trace_id: string → generated UUID if missing
  - response_version: string → enforced "v1"
- Implementation: [response_composer.py](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/app/core/response_composer.py#L196-L212)

## Lifecycle States (Internal Mapping)
- Task Created
- Task Scheduled
- Task Deferred
- Task Failed
- Clarification Needed
- Default
Note: State is inferred from inputs; state name is not part of the payload to keep the surface minimal.

## Schema (JSON)
```json
{
  "assistant_message": "string",
  "action_taken": "string",
  "next_steps": ["string"],
  "confidence_level": "high" | "medium" | "low",
  "trace_id": "string",
  "response_version": "v1"
}
```

## Example
```json
{
  "assistant_message": "I've scheduled your meeting for tomorrow at 2pm.",
  "action_taken": "Scheduled meeting.",
  "next_steps": ["Check calendar", "Confirm attendees"],
  "confidence_level": "high",
  "trace_id": "db9f789a-e145-46c2-a087-3534d907a770",
  "response_version": "v1"
}
```

## UI Consumption Guide
- Render assistant_message as primary content
- Optionally show action_taken as a small status/footer
- Display next_steps as tappable chips or buttons
- Optionally highlight confidence_level when "low"
- Log trace_id for telemetry; do not display to users
- Require response_version === "v1"; if not, fallback to safe display

## Backend Consumption Guide
- Treat ARL payload as the canonical response boundary
- Validate required fields and enums; ignore unknown extras
- Do not rely on upstream internals (Summary/Intent/Task/Decision)
- Use trace_id for request correlation in logs/metrics
- Gate by response_version === "v1" and prepare migration path for future versions

## Verification
- Unit contract tests:
  - [test_response_composer.py](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/tests/test_response_composer.py)
  - [test_regression.py](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/tests/test_regression.py)

