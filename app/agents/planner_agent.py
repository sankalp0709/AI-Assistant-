import json
import re
from .base_agent import BaseAgent

class PlannerAgent(BaseAgent):
    name = "planner"

    async def run(self, query, context):
        prompt = f"""
        You are the Planner Agent for a sophisticated AI Assistant.
        Your goal is to break down the user's request into logical, executable steps.
        
        User Query: "{query}"
        Context: {context}
        
        Available Step Types:
        - research: Gathering information from web or tools.
        - analyze: Processing data or making decisions.
        - execute: Performing an action (e.g., sending email, creating file).
        
        Output format must be strictly JSON:
        {{
            "steps": [
                {{"type": "research", "description": "Search for X"}},
                {{"type": "analyze", "description": "Summarize X"}},
                {{"type": "execute", "description": "Email X to Y"}}
            ]
        }}
        
        Do not include markdown code blocks. Output ONLY raw JSON.
        """
        
        raw_response = await self.call_llm(prompt)
        
        # Clean response (remove markdown if present)
        cleaned_response = re.sub(r"```json\s*|\s*```", "", raw_response).strip()
        
        try:
            plan = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            plan = {
                "steps": [
                    {"type": "analyze", "description": f"Failed to parse plan. Raw: {raw_response[:50]}..."}
                ]
            }
            
        return {"agent": self.name, "output": plan}