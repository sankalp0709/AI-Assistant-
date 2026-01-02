const { composeAssistantResponse } = require('../node/response_composer')

function assert(cond, msg) {
  if (!cond) {
    console.error('FAIL:', msg)
    process.exit(1)
  }
}

function testConfidenceFromTrust() {
  const payload = {
    summary: {},
    task: {},
    routing: { trust: { confidence: 0.9, confidence_verified: true } },
    execution_status: { status: 'success' },
  }
  const out = composeAssistantResponse(payload)
  assert(out.confidence_level === 'high', 'confidence_level should be high when trust.confidence=0.9 verified')
  assert(out.response_version === 'v1', 'response_version should be v1')
}

function testVerifiedTrace() {
  const payload = {
    summary: {},
    task: {},
    routing: {},
    execution_status: { status: 'success', trust: { trace_ref: 'trusted-xyz', trace_ref_verified: true } },
  }
  const out = composeAssistantResponse(payload)
  assert(out.trace_id === 'trusted-xyz', 'trace_id should equal verified trust trace_ref')
}

function main() {
  testConfidenceFromTrust()
  testVerifiedTrace()
  console.log('OK Node trust tests')
}

main()
