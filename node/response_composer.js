function composeAssistantResponse({ summary = {}, task = {}, routing = {}, execution_status = { status: "success" } }) {
  const templates = {
    task_created: {
      message_template: "I've created a {task_type} task for you: {description}.",
      action_template: "Created {task_type} task with priority {priority}.",
      next_steps: ["Review task details", "Modify if needed"],
    },
    task_scheduled: {
      message_template: "I've scheduled your {task_type} for {datetime}.",
      action_template: "Scheduled {task_type} at {datetime}.",
      next_steps: ["Check calendar", "Set reminder"],
    },
    task_deferred: {
      message_template: "I've noted that down but haven't scheduled it yet.",
      action_template: "Deferred task creation.",
      next_steps: ["Provide time to schedule", "Add more details"],
    },
    task_failed: {
      message_template: "I encountered an issue while processing your request.",
      action_template: "Failed to execute task: {error_reason}.",
      next_steps: ["Retry with clear instructions", "Check system status"],
    },
    clarification_needed: {
      message_template: "I need a bit more information to proceed. {clarification_prompt}",
      action_template: "Requested clarification.",
      next_steps: ["Provide missing details"],
    },
    default: {
      message_template: "{response_text}",
      action_template: "Processed request.",
      next_steps: [],
    },
  };

  function determineScenario(task, execution_status, routing) {
    const status = execution_status?.status;
    const needsClar = execution_status?.requires_clarification === true || task?.requires_clarification === true;
    if (status === "error") return "task_failed";
    if (status === "clarification_needed" || needsClar) return "clarification_needed";
    if (execution_status?.deferred) return "task_deferred";
    if (task && task.task_type) {
      const params = task.parameters || {};
      if (params.datetime) return "task_scheduled";
      return "task_created";
    }
    return "default";
  }

  function prepareContext(summary, task, routing, execution_status) {
    const ctx = {
      task_type: "task",
      description: "item",
      priority: "normal",
      datetime: "unspecified time",
      error_reason: "unknown error",
      clarification_prompt: "Could you provide more details?",
      response_text: "I processed your request.",
    };
    if (task) {
      ctx.task_type = task.task_type || "task";
      ctx.priority = task.priority || "normal";
      const params = task.parameters || {};
      ctx.description = params.message || params.query || "item";
      ctx.datetime = params.datetime || "unspecified time";
    }
    if (summary && ctx.description === "item") {
      ctx.description = summary.summary || "item";
    }
    if (execution_status) {
      ctx.error_reason = execution_status.error || "unknown error";
      ctx.clarification_prompt = execution_status.clarification_prompt || "Could you provide more details?";
    }
    if (routing) {
      ctx.response_text = "I processed your request.";
    }
    return ctx;
  }

  function calculateConfidence(task, routing, execution_status) {
    const trust = (execution_status && execution_status.trust) || (routing && routing.trust) || {};
    if (trust && trust.confidence_verified === true && typeof trust.confidence === 'number') {
      const tval = Number(trust.confidence);
      if (!isFinite(tval)) return "medium";
      if (tval <= 0.4) return "low";
      if (tval <= 0.7) return "medium";
      return "high";
    }
    const confVal = (task && task.confidence) || (routing && routing.confidence) || 1.0;
    const val = Number(confVal);
    if (!isFinite(val)) return "medium";
    if (val >= 0.8) return "high";
    if (val >= 0.5) return "medium";
    return "low";
  }

  function validateOutput(data) {
    const msg = data.assistant_message;
    data.assistant_message = typeof msg === "string" && msg.trim() ? msg : "I processed your request.";
    const act = data.action_taken;
    data.action_taken = typeof act === "string" && act.trim() ? act : "Processed request.";
    const steps = data.next_steps;
    data.next_steps = Array.isArray(steps) ? steps : [];
    const conf = data.confidence_level;
    data.confidence_level = ["high", "medium", "low"].includes(conf) ? conf : "medium";
    const tid = data.trace_id;
    data.trace_id = typeof tid === "string" && tid ? tid : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const ver = data.response_version;
    data.response_version = typeof ver === "string" && ver ? ver : "v1";
    return data;
  }

  // Trace ID consistency: Look in all inputs
  const trustBlock = (execution_status && execution_status.trust) || (routing && routing.trust) || {};
  const trace_id =
    (typeof (trustBlock && (trustBlock.trace_ref || trustBlock.trace_reference)) === 'string' && (trustBlock.trace_ref || trustBlock.trace_reference)) ||
    (routing && typeof routing.verified_trace_id === 'string' && routing.verified_trace_id) ||
    (execution_status && typeof execution_status.verified_trace_id === 'string' && execution_status.verified_trace_id) ||
    (execution_status && execution_status.trace_id) ||
    (task && task.trace_id) ||
    (summary && summary.trace_id) ||
    (routing && routing.trace_id) ||
    `${Date.now()}-${Math.random().toString(36).slice(2)}`;

  try {
    // Input type validation to ensure consistency with Python
    if (task && typeof task !== 'object') throw new Error("Invalid task format");
    if (summary && typeof summary !== 'object') throw new Error("Invalid summary format");
    if (routing && typeof routing !== 'object') throw new Error("Invalid routing format");
    if (execution_status && typeof execution_status !== 'object') throw new Error("Invalid execution_status format");

    const scenario = determineScenario(task, execution_status, routing);
    const template = templates[scenario] || templates.default;
    const ctx = prepareContext(summary, task, routing, execution_status);
    const assistant_message = template.message_template.replace(/\{(\w+)\}/g, (_, k) => String(ctx[k] || ""));
    const action_taken = template.action_template.replace(/\{(\w+)\}/g, (_, k) => String(ctx[k] || ""));
    const next_steps = template.next_steps;
    const confidence_level = calculateConfidence(task, routing, execution_status);
    
    return validateOutput({
      assistant_message,
      action_taken,
      next_steps,
      confidence_level,
      trace_id,
      response_version: "v1",
    });
  } catch (error) {
    // Fallback for unexpected failures
    return validateOutput({
      assistant_message: "I encountered an internal error while processing your request.",
      action_taken: "System error caught during response composition.",
      next_steps: ["Retry request", "Contact support"],
      confidence_level: "low",
      trace_id,
      response_version: "v1",
    });
  }
}

module.exports = { composeAssistantResponse };
