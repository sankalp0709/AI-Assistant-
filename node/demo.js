const { composeAssistantResponse } = require('./response_composer');

const cases = [
  { summary: { summary: "Buy milk" }, task: {}, routing: {}, execution_status: { status: "success" } },
  { summary: {}, task: { task_type: "reminder", parameters: { message: "buy milk" }, priority: "normal" }, routing: {}, execution_status: null },
  { summary: {}, task: {}, routing: { response: "Hello", confidence: 0.9 }, execution_status: { status: "success" } },
  { summary: {}, task: {}, routing: { confidence: 0.6 }, execution_status: { status: "success" } },
  { summary: {}, task: {}, routing: {}, execution_status: { status: "clarification_needed", clarification_prompt: "Specify date" } }
];

for (const payload of cases) {
  const out = composeAssistantResponse(payload);
  console.log(JSON.stringify(out, null, 2));
}
