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
  const name = taskName(payload)
  if (status === 'created') {
    return {
      assistant_message: name ? 'Task created. ' + name + '.' : 'Task created.',
      action_taken: 'Created task',
      next_steps: ['Begin execution', 'Monitor progress'],
      confidence_level: normalizeConfidence(payload),
      trace_id: resolveTraceId(payload),
    }
  }
  if (status === 'scheduled') {
    return {
      assistant_message: name ? 'Task scheduled. ' + name + '.' : 'Task scheduled.',
      action_taken: 'Scheduled task',
      next_steps: ['Await schedule', 'Confirm start'],
      confidence_level: normalizeConfidence(payload),
      trace_id: resolveTraceId(payload),
    }
  }
  if (status === 'deferred') {
    return {
      assistant_message: name ? 'Task deferred. ' + name + '.' : 'Task deferred.',
      action_taken: 'Deferred task',
      next_steps: ['Resolve blockers', 'Reschedule'],
      confidence_level: normalizeConfidence(payload),
      trace_id: resolveTraceId(payload),
    }
  }
  if (status === 'failed') {
    return {
      assistant_message: name ? 'Task failed. ' + name + '.' : 'Task failed.',
      action_taken: 'Recorded failure',
      next_steps: ['Review cause', 'Apply fix', 'Retry'],
      confidence_level: normalizeConfidence(payload),
      trace_id: resolveTraceId(payload),
    }
  }
  return {
    assistant_message: name ? 'Clarification needed. ' + name + '.' : 'Clarification needed.',
    action_taken: 'Requested clarification',
    next_steps: ['Provide missing details', 'Confirm scope'],
    confidence_level: normalizeConfidence(payload),
    trace_id: resolveTraceId(payload),
  }
}
function composeAssistantResponse(payload) {
  const status = normalizeStatus(payload)
  const tpl = templates(status, payload)
  return {
    assistant_message: tpl.assistant_message,
    action_taken: tpl.action_taken,
    next_steps: tpl.next_steps,
    confidence_level: tpl.confidence_level,
    trace_id: tpl.trace_id,
  }
}
module.exports = { composeAssistantResponse }
