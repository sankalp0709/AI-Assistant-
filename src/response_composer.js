function get(obj, path) {
  return path.split('.').reduce((o, k) => (o && o[k] !== undefined ? o[k] : undefined), obj)
}
function toString(x) {
  if (x === undefined || x === null) return ''
  if (typeof x === 'string') return x
  return String(x)
}
function stableId(s) {
  let h = 0
  for (let i = 0; i < s.length; i++) {
    h = (h * 31 + s.charCodeAt(i)) >>> 0
  }
  return h.toString(16)
}
function normalizeStatus(payload) {
  const es = payload && payload.execution_status ? payload.execution_status : {}
  const t = payload && payload.task ? payload.task : {}
  const r = payload && payload.routing ? payload.routing : {}
  const explicit = toString(es.status || t.status || r.status).toLowerCase()
  const needsClar = es.requires_clarification === true || t.requires_clarification === true
  if (needsClar) return 'clarification_needed'
  if (explicit === 'clarification_needed') return 'clarification_needed'
  if (explicit === 'failed') return 'failed'
  if (explicit === 'deferred') return 'deferred'
  if (explicit === 'scheduled') return 'scheduled'
  if (explicit === 'created' || explicit === 'new' || explicit === 'ready') return 'created'
  if (es.error || es.failure || es.reason) return 'failed'
  return 'created'
}
function normalizeConfidence(payload) {
  const es = payload && payload.execution_status ? payload.execution_status : {}
  const s = payload && payload.summary ? payload.summary : {}
  const trust = (es && es.trust) || (payload && payload.routing && payload.routing.trust) || {}
  if (trust && trust.confidence_verified === true && typeof trust.confidence === 'number') {
    const num = trust.confidence
    if (num <= 0.4) return 'low'
    if (num <= 0.7) return 'medium'
    return 'high'
  }
  const str = toString(es.confidence_level || s.confidence_level).toLowerCase()
  if (str === 'low' || str === 'medium' || str === 'high') return str
  const num = typeof es.confidence === 'number' ? es.confidence : typeof s.confidence === 'number' ? s.confidence : undefined
  if (typeof num === 'number') {
    if (num <= 0.4) return 'low'
    if (num <= 0.7) return 'medium'
    return 'high'
  }
  return 'medium'
}
function resolveTraceId(payload) {
  const r = payload && payload.routing ? payload.routing : {}
  const es = payload && payload.execution_status ? payload.execution_status : {}
  const t = payload && payload.task ? payload.task : {}
  const trust = (es && es.trust) || (r && r.trust) || {}
  const verified = toString(
    (trust && (trust.trace_ref || trust.trace_reference)) ||
    r.verified_trace_id ||
    es.verified_trace_id
  )
  if (verified) return verified
  const direct = toString(r.trace_id || es.trace_id || t.trace_id || t.id)
  if (direct) return direct
  const base = JSON.stringify(payload)
  return stableId(base)
}
function taskName(payload) {
  const t = payload && payload.task ? payload.task : {}
  return toString(t.name || t.title || t.display_name || t.label)
}
function templates(status, payload) {
  const t = payload && payload.task ? payload.task : {}
  const es = payload && payload.execution_status ? payload.execution_status : {}

  const taskType = toString(t.task_type || 'task')
  const description = toString(t.description || t.name || t.title || t.display_name || t.label || 'item')
  const priority = toString(t.priority || 'normal')
  const params = t.parameters || {}
  const datetime = toString(params.datetime || t.datetime || 'unspecified time')
  const errorReason = toString(es.error || es.failure || es.reason || 'unknown error')
  const clarificationPrompt = toString(es.clarification_prompt || t.clarification_prompt || 'Could you provide more details?')

  if (status === 'created') {
    return {
      assistant_message: "I've created a " + taskType + " task for you: " + description + ".",
      action_taken: "Created " + taskType + " task with priority " + priority + ".",
      next_steps: ['Review task details', 'Modify if needed'],
      confidence_level: normalizeConfidence(payload),
      trace_id: resolveTraceId(payload),
    }
  }
  if (status === 'scheduled') {
    return {
      assistant_message: "I've scheduled your " + taskType + " for " + datetime + ".",
      action_taken: "Scheduled " + taskType + " at " + datetime + ".",
      next_steps: ['Check calendar', 'Set reminder'],
      confidence_level: normalizeConfidence(payload),
      trace_id: resolveTraceId(payload),
    }
  }
  if (status === 'deferred') {
    return {
      assistant_message: "I've noted that down but haven't scheduled it yet.",
      action_taken: "Deferred task creation.",
      next_steps: ['Provide time to schedule', 'Add more details'],
      confidence_level: normalizeConfidence(payload),
      trace_id: resolveTraceId(payload),
    }
  }
  if (status === 'failed') {
    return {
      assistant_message: "I encountered an issue while processing your request.",
      action_taken: "Failed to execute task: " + errorReason + ".",
      next_steps: ['Retry with clear instructions', 'Check system status'],
      confidence_level: normalizeConfidence(payload),
      trace_id: resolveTraceId(payload),
    }
  }
  return {
    assistant_message: "I need a bit more information to proceed. " + clarificationPrompt,
    action_taken: "Requested clarification.",
    next_steps: ['Provide missing details'],
    confidence_level: normalizeConfidence(payload),
    trace_id: resolveTraceId(payload),
  }
}
function composeAssistantResponse(payload) {
  const status = normalizeStatus(payload)
  const tpl = templates(status, payload)
  const out = {
    assistant_message: tpl.assistant_message,
    action_taken: tpl.action_taken,
    next_steps: tpl.next_steps,
    confidence_level: tpl.confidence_level,
    trace_id: tpl.trace_id,
  }
  const msg = toString(out.assistant_message)
  out.assistant_message = msg && msg.trim() ? msg : 'I processed your request.'
  const act = toString(out.action_taken)
  out.action_taken = act && act.trim() ? act : 'Processed request.'
  out.next_steps = Array.isArray(out.next_steps) ? out.next_steps : []
  const conf = toString(out.confidence_level).toLowerCase()
  out.confidence_level = conf === 'high' || conf === 'medium' || conf === 'low' ? conf : 'medium'
  const tid = toString(out.trace_id)
  out.trace_id = tid || stableId(JSON.stringify(payload || {}))
  out.response_version = 'v1'
  return out
}
module.exports = { composeAssistantResponse }
