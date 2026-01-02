const fs = require('fs');
const path = require('path');
const { composeAssistantResponse } = require('./response_composer');

const dataPath = path.join(__dirname, '../tests/regression_data.json');
const testCases = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

let passed = 0;
let failed = 0;

console.log(`Running ${testCases.length} regression tests...`);

testCases.forEach(testCase => {
  console.log(`\nCase: ${testCase.name}`);
  const input = testCase.input;
  
  // Adapt input for JS function (it expects named args in object)
  const args = {
    summary: input.summary,
    task: input.task,
    routing: input.routing,
    execution_status: input.execution_status
  };

  const result = composeAssistantResponse(args);
  
  let casePassed = true;
  const expected = testCase.expected_partial;
  
  for (const [key, val] of Object.entries(expected)) {
    if (result[key] !== val) {
      console.error(`  Mismatch in ${key}: expected "${val}", got "${result[key]}"`);
      casePassed = false;
    }
  }
  
  // Mandatory fields check
  const mandatory = ["assistant_message", "action_taken", "next_steps", "confidence_level", "trace_id", "response_version"];
  mandatory.forEach(field => {
    if (result[field] === undefined) {
      console.error(`  Missing mandatory field: ${field}`);
      casePassed = false;
    }
  });

  if (result.response_version !== "v1") {
    console.error(`  Invalid version: ${result.response_version}`);
    casePassed = false;
  }

  if (casePassed) {
    console.log("  PASS");
    passed++;
  } else {
    console.log("  FAIL");
    failed++;
  }
});

console.log(`\nSummary: ${passed} passed, ${failed} failed.`);
if (failed > 0) process.exit(1);
