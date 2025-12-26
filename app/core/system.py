from .bhiv_core import BHIVCore
from .bhiv_reasoner import BHIVReasoner
from .decision_hub import DecisionHub
from ..memory.memory_manager import MemoryManager
from ..agents.planner_agent import PlannerAgent
from ..agents.researcher_agent import ResearcherAgent
from ..agents.analyst_agent import AnalystAgent
from ..agents.executor_agent import ExecutorAgent
from ..agents.evaluator_agent import EvaluatorAgent
from ..tools.search_tool import SearchTool
from ..tools.web_browser_tool import WebBrowserTool
from ..tools.calculator_tool import CalculatorTool
from ..tools.file_tool import FileTool
from ..tools.automation_tool import AutomationTool

# Initialize Components
memory_manager = MemoryManager()

agents = {
    "planner": PlannerAgent(),
    "researcher": ResearcherAgent(),
    "analyst": AnalystAgent(),
    "executor": ExecutorAgent(),
    "evaluator": EvaluatorAgent()
}

tools = {
    "search": SearchTool(),
    "web_browser": WebBrowserTool(),
    "calculator": CalculatorTool(),
    "file": FileTool(),
    "automation": AutomationTool()
}

reasoner = BHIVReasoner()

# Global System Instances
bhiv = BHIVCore(memory_manager, agents, tools, reasoner)
decision_hub = DecisionHub()
