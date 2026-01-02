import asyncio
import sys
import os

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.system import bhiv

async def main():
    print("Starting Phase 2 Verification...")
    
    # Mock BHIVInput as defined in DecisionHub
    class BHIVInput:
        def __init__(self, query, context):
            self.query = query
            self.context = context
            
        def __str__(self):
            return self.query
    
    query = "Research the benefits of Vitamin D."
    input_data = BHIVInput(query=query, context={"user_id": "test_user"})
    
    print(f"Processing query: {query}")
    try:
        # This will trigger:
        # 1. BHIVCore.process
        # 2. BHIVReasoner.run
        # 3. PlannerAgent.run (LLM call -> Plan)
        # 4. Loop over steps -> ResearcherAgent.run (SearchTool + LLM call)
        # 5. EvaluatorAgent.run (LLM call -> Final Answer)
        
        result = await bhiv.process(input_data)
        
        print("\n✅ BHIV Process Result:")
        # Evaluator returns {"agent": "evaluator", "output": "..."}
        # BHIVReasoner.finalize returns result["output"]
        print(result) 
        
        if isinstance(result, str) and len(result) > 10:
             print("\n✅ Verification SUCCESS: Received a substantial string response.")
        else:
             print("\n⚠️ Verification WARNING: Response seems short or unexpected.")
             
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
