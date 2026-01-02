from .base_agent import BaseAgent

class ResearcherAgent(BaseAgent):
    name = "researcher"

    async def run(self, task, context, tools=None):
        """
        Execute research task.
        task: dict with 'description'
        context: dict
        tools: dict of available tools
        """
        query = task.get("description", "")
        search_results = "No tools available for search."
        
        if tools and "search" in tools:
            try:
                # Assuming SearchTool has a run method taking a query string
                search_results = await tools["search"].run(query)
            except Exception as e:
                search_results = f"Search failed: {e}"
        
        # Summarize findings with LLM
        prompt = f"""
        You are the Researcher Agent.
        Goal: {query}
        Context: {context}
        Search Results: {search_results}
        
        Summarize the findings relevant to the goal.
        """
        
        summary = await self.call_llm(prompt)
        return {"agent": self.name, "output": summary}