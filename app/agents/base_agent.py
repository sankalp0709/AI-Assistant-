import logging
from ..core.llm_bridge import llm_bridge

logger = logging.getLogger(__name__)

class BaseAgent:
    name = "base"

    def __init__(self):
        self.llm = llm_bridge

    async def run(self, query, context):
        raise NotImplementedError("Agents must implement run()")

    async def call_llm(self, prompt: str, model: str = "chatgpt") -> str:
        try:
            return await self.llm.call_llm(model, prompt)
        except Exception as e:
            logger.error(f"LLM call failed in {self.name}: {e}")
            return f"Error processing request: {e}"