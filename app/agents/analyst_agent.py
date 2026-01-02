from .base_agent import BaseAgent

class AnalystAgent(BaseAgent):
    name = "analyst"

    async def run(self, task, context, tools=None):
        """
        Analyze data or content.
        """
        query = task.get("description", "")
        
        prompt = f"""
        You are the Analyst Agent.
        Your goal is to analyze the following topic/data.
        
        Topic: {query}
        Context: {context}
        
        Provide a detailed analysis, identifying key patterns, pros/cons, or insights.
        """
        
        analysis = await self.call_llm(prompt)
        return {"agent": self.name, "output": analysis}