from .base_agent import BaseAgent

class EvaluatorAgent(BaseAgent):
    name = "evaluator"

    async def run(self, steps, context):
        """
        Synthesize findings from all previous steps into a final answer.
        """
        prompt = f"""
        You are the Evaluator Agent.
        Your goal is to synthesize the following execution steps into a final, coherent response for the user.
        
        User Context: {context}
        
        Execution Steps & Findings:
        {steps}
        
        Provide a final answer that directly addresses the user's intent.
        """
        
        final_response = await self.call_llm(prompt)
        return {"agent": self.name, "output": final_response}