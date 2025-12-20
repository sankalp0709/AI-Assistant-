# Assistant Backend API Contract

## Overview
This document defines the contract for the Assistant Backend API, specifically the `/api/assistant` endpoint. This endpoint serves as the single entry point for the AI Assistant, handling user inputs and orchestrating the full processing pipeline.

## Endpoint
- **URL**: `POST /api/assistant`
- **Authentication**: Required via `X-API-Key` header
- **Content-Type**: `application/json`

## Request Format

### Schema
```json
{
  "message": "string (optional)",
  "summarized_payload": {
    "summary": "string",
    "key_points": ["string"],
    "entities": {},
    "word_count": 0,
    "sentence_count": 0,
    "timestamp": "ISO 8601 string",
    "version": "string"
  } (optional),
  "platform": "string (default: 'web')",
  "device_context": "string (default: 'desktop')",
  "voice_input": "boolean (default: false)"
}
```

### Validation Rules
- Either `message` OR `summarized_payload` must be provided
- If `summarized_payload` is provided, it must contain a `summary` field
- All other fields are optional with defaults

### Request Examples

#### Example 1: Raw User Message
```bash
curl -X POST "https://your-backend-url/api/assistant" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "message": "Summarize this meeting about AI development",
    "platform": "web",
    "device_context": "desktop"
  }'
```

#### Example 2: Pre-summarized Payload
```bash
curl -X POST "https://your-backend-url/api/assistant" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "summarized_payload": {
      "summary": "Create a reminder for the meeting tomorrow",
      "key_points": ["Meeting reminder"],
      "entities": {},
      "word_count": 5,
      "sentence_count": 1,
      "timestamp": "2025-12-20T15:13:00",
      "version": "summaryflow_v1"
    },
    "platform": "mobile",
    "device_context": "android"
  }'
```

## Response Format

### Success Response Schema
```json
{
  "status": "success",
  "data": {
    "summary": {
      "summary": "string",
      "key_points": ["string"],
      "entities": {},
      "word_count": 0,
      "sentence_count": 0,
      "timestamp": "ISO 8601 string",
      "version": "string"
    },
    "intent": {
      "intent": "string",
      "entities": {},
      "dates_times": {},
      "context": {},
      "confidence": 0.0,
      "timestamp": "ISO 8601 string",
      "version": "string",
      "original_text": "string"
    },
    "task": {
      "task_type": "string",
      "parameters": {},
      "priority": "string",
      "confidence": 0.0,
      "timestamp": "ISO 8601 string",
      "version": "string"
    },
    "decision": {
      "final_decision": "string",
      "confidence": 0.0,
      "selected_agent": "string",
      "preferred_llm": "string",
      "device_context": "string",
      "memory_reference": null,
      "intent": "string",
      "processed_text": "string",
      "response": "string (optional)",
      "task_created": {} (optional),
      "voice_output": {} (optional)
    },
    "processed_at": "ISO 8601 string"
  },
  "error": null
}
```

### Error Response Schema
```json
{
  "status": "error",
  "data": {},
  "error": "string"
}
```

## Field Specifications

### Fields Frontend MUST Rely On

#### Status Indication
- `status`: Always check this first. Values: `"success"` or `"error"`

#### Core Processing Results
- `data.summary.summary`: The processed/summarized text for display
- `data.intent.intent`: Primary intent classification (e.g., "task", "summarize", "general")
- `data.task.task_type`: Structured task type if applicable
- `data.decision.final_decision`: The routing decision made by the system
- `data.decision.response`: Generated response text (if available)
- `data.decision.task_created`: Task creation confirmation (if task was created)

#### Metadata
- `data.processed_at`: Timestamp of processing completion

### Fields Frontend MUST Ignore

#### Internal Processing Details
- `data.summary.key_points`: Implementation detail, may change
- `data.summary.entities`: Internal entity extraction
- `data.summary.word_count`: Statistical metadata
- `data.summary.sentence_count`: Statistical metadata
- `data.summary.timestamp`: Internal processing timestamp
- `data.summary.version`: Version info, subject to change

#### Intent Processing Internals
- `data.intent.entities`: Raw entity data
- `data.intent.dates_times`: Date/time parsing details
- `data.intent.context`: Internal context analysis
- `data.intent.confidence`: Confidence scores (unstable)
- `data.intent.timestamp`: Internal timestamp
- `data.intent.version`: Version info
- `data.intent.original_text`: Duplicate of input

#### Task Processing Internals
- `data.task.parameters`: Internal parameter mapping
- `data.task.priority`: Internal priority calculation
- `data.task.confidence`: Confidence scores
- `data.task.timestamp`: Internal timestamp
- `data.task.version`: Version info

#### Decision Processing Internals
- `data.decision.confidence`: Confidence scores
- `data.decision.selected_agent`: Agent selection details
- `data.decision.preferred_llm`: LLM selection details
- `data.decision.device_context`: Context info
- `data.decision.memory_reference`: Memory system details
- `data.decision.intent`: Duplicate of intent.intent
- `data.decision.processed_text`: Processed text
- `data.decision.voice_output`: Voice processing details

## Error Handling

### Common Error Messages
- `"Invalid input: Either message or summarized_payload with summary field must be provided"`: Missing required input
- `"Summary processing failed"`: Internal summary generation error
- `"Intent detection failed"`: NLU processing error
- `"Task creation failed"`: Task mapping error
- `"Decision processing failed"`: Routing/orchestration error
- `"Internal processing error"`: Generic fallback error

### Error Response Handling
- Always check `status === "error"`
- Display `error` message to user
- `data` will be empty object `{}` on error
- Do not attempt to parse `data` when `status` is `"error"`

## Processing Pipeline

The endpoint orchestrates this internal flow:
1. **SummaryFlow**: Generate/extract summary from input
2. **IntentFlow**: Classify intent and extract entities
3. **TaskFlow**: Map to structured task if applicable
4. **Decision Hub**: Route to appropriate handler (simple response vs BHIV complex processing)

## Versioning
- This contract is for API version 3.0.0
- Breaking changes will be communicated with version bumps
- Fields marked as "MUST ignore" may change without notice

## Rate Limiting
- Subject to backend rate limiting
- Check response status codes (429 for rate limited)
- Implement exponential backoff for retries

## Support
For integration issues, contact the backend team with:
- Request payload used
- Full response received
- Timestamp of request
- Platform/device context