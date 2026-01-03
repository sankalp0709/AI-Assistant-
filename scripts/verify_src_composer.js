const { composeAssistantResponse } = require('../src/response_composer');

const payload = {
  execution_status: {
    status: 'clarification_needed',
    clarification_prompt: 'What is the date?'
  }
};

const result = composeAssistantResponse(payload);

console.log('Message:', result.assistant_message);

if (result.assistant_message === 'I need a bit more information to proceed. What is the date?') {
  console.log('PASS');
} else {
  console.log('FAIL');
  console.log('Expected: I need a bit more information to proceed. What is the date?');
  console.log('Actual:', result.assistant_message);
  process.exit(1);
}
