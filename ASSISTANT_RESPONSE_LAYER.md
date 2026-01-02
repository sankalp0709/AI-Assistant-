# Assistant Response Layer (ARL): Formal Contract Specification

## Contract Overview
- Purpose: Provide deterministic, frontend-ready responses that are stable across releases
- Scope: Final boundary output from ARL, produced by [response_composer.py](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/app/core/response_composer.py)
- Versioning: All outputs MUST include `response_version` and currently lock to `"v1"`
- Determinism: Output strings and enums derive from fixed templates; no free-form LLM text is used

## Required Fields
- `assistant_message` (string) — human-readable main message. Non-empty; falls back to safe default
- `action_taken` (string) — concise system action summary. Non-empty; falls back to safe default
- `next_steps` (array<string>) — follow-up suggestions as short imperative phrases
- `confidence_level` (enum) — one of: `"high"`, `"medium"`, `"low"`
- `trace_id` (string) — UUID or externally provided ID that traces this response
- `response_version` (string) — current fixed contract version: `"v1"`

## Optional Fields
- None. The ARL contract is intentionally minimal and closed to prevent accidental surface expansion

## Never Allowed Fields
- Any internal processing details from upstream flows:
  - Summary internals: `key_points`, `entities`, `word_count`, `sentence_count`, `timestamp`, `version`
  - Intent internals: `entities`, `dates_times`, `context`, `confidence`, `timestamp`, `version`, `original_text`
  - Task internals: `parameters`, `priority`, `confidence`, `timestamp`, `version`
  - Decision internals: `confidence`, `selected_agent`, `preferred_llm`, `device_context`, `memory_reference`, `intent`, `processed_text`, `voice_output`
- Any LLM or agent metadata:
  - Model names, provider identifiers, prompts, temperature/top-p settings, stop sequences, token counts
  - Agent names, chain-of-thought, intermediate steps, tool call parameters
- Debug, tracing, or server-side details:
  - Stack traces, exception messages, environment variables, log lines, Sentry IDs
  - File paths, DB references, internal IDs (except `trace_id`)

## Strict Determinism Guarantee
- Outputs are produced via fixed templates that map upstream states to bounded strings and enums
- All fields undergo type validation and fallbacks in [response_composer.py](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/app/core/response_composer.py#L196-L212)
- No external model calls are made in ARL; content is formatted with `.format(**context)` using constrained context variables
- Allowed enums and defaults:
  - `confidence_level`: `"high" | "medium" | "low"`; fallback `"medium"`
  - `next_steps`: array<string>; fallback `[]`
  - `assistant_message`: string; fallback `"I processed your request."`
  - `action_taken`: string; fallback `"Processed request."`
  - `trace_id`: string; generated UUID if missing
  - `response_version`: string; enforced `"v1"`

## Lifecycle States
ARL templates cover these deterministic scenarios. States are inferred from inputs but not exposed as a field:
- Task Created — a task exists without scheduling details
- Task Scheduled — a task includes specific `datetime`
- Task Deferred — processing intentionally deferred
- Task Failed — execution error encountered
- Clarification Needed — additional user input required
- Default — generic response when none of the above apply

## Output Schema (v1)
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

## Example Outputs
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

## Validation Rules
- Enforce required fields and types exactly
- Reject or strip any never-allowed fields before consumption
- Do not rely on upstream internals; ARL is the sole boundary for UI consumption
- Always gate by `response_version === "v1"`

## Frontend Consumption Guide
- Render `assistant_message` as the primary content
- Show `action_taken` as a small status/footer if desired
- Display `next_steps` as tappable chips or buttons
- Optionally surface `confidence_level` as a badge; emphasize when `"low"`
- Log `trace_id` for telemetry; do not show it to users
- Require `response_version === "v1"`; if not, fallback to a safe display path

## Backend Consumption Guide
- Treat ARL output as the single canonical response payload
- Do not bind UI to upstream internals (Summary/Intent/Task/Decision)
- Validate required fields and enums; ignore any extra/unknown fields
- Use `trace_id` for correlation across logs/metrics
- Version-lock to `"v1"` and apply migration logic only when a future version is introduced

## Operational Notes
- Adding new scenarios requires updating templates and tests only; no schema change
- Extending the schema is prohibited without product approval and a version bump
- Contract tests live in [test_response_composer.py](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/tests/test_response_composer.py) and [test_regression.py](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/tests/test_regression.py)

## Trust Readiness (Quiet)
- Input hooks: pass verified trust inputs via `routing.trust` or `execution_status.trust`
- Verified confidence: when `confidence_verified` is true, numeric `confidence` overrides mapping to produce `"high"|"medium"|"low"`
- Verified trace: when `trace_ref_verified` is true, `trace_ref` is passed through to `trace_id`
- Authenticity tags: accepted via input but not exposed in ARL output (placeholder only)
- Implementation: see [response_composer.py](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/app/core/response_composer.py#L70-L106)

## Integration Guidelines
- Backend
  - Produce ARL payload with [compose_response](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/app/core/response_composer.py#L45-L145)
  - Include verified trust signals when available; ARL ingests quietly and enforces determinism
  - Validate `response_version === "v1"` and required fields before UI consumption
- Clients
  - Bind UI strictly to ARL output fields
  - Do not depend on upstream internals; treat ARL as the canonical boundary

## Usage (Node)
- Module: [response_composer.js](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/src/response_composer.js)
- Export: `composeAssistantResponse(payload)`
- Input schema:
  - `{ summary: {}, task: {}, routing: {}, execution_status: {} }`
- Output schema:
  - `{ assistant_message, action_taken, next_steps[], confidence_level, trace_id, response_version }`
- Failure behavior:
  - Validates and falls back to safe defaults for strings, enums, arrays
  - Always sets `response_version: "v1"`
- Demo: [node/demo.js](file:///c:/Users/user11/Desktop/int/AI_ASSISTANT_PhaseB_Integration/node/demo.js)

## E2E Verification
- Start local server: `uvicorn app.main:app --host 127.0.0.1 --port 8000`
- Ensure `X-API-Key` header matches environment `API_KEY`
- Run script: `python scripts/verify_integration.py`
- Verification checks required fields and enforces `response_version: "v1"` for the returned payload
