const fs = require('fs')
const path = require('path')
const { composeAssistantResponse } = require('../src/response_composer')
function loadJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'))
}
function runOne(payloadPath, outputPath) {
  const payload = loadJson(payloadPath)
  const output = composeAssistantResponse(payload)
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2))
  process.stdout.write(`OK ${path.basename(payloadPath)} -> ${path.basename(outputPath)}\n`)
}
function main() {
  const pairs = [
    ['examples/payload_task_created.json', 'examples/output_task_created.json'],
    ['examples/payload_task_scheduled.json', 'examples/output_task_scheduled.json'],
    ['examples/payload_task_deferred.json', 'examples/output_task_deferred.json'],
    ['examples/payload_task_failed.json', 'examples/output_task_failed.json'],
    ['examples/payload_clarification_needed.json', 'examples/output_clarification_needed.json'],
    ['examples/payload_default.json', 'examples/output_default.json'],
  ]
  for (const [p, o] of pairs) runOne(path.resolve(__dirname, '..', p), path.resolve(__dirname, '..', o))
}
main()
