"""
Agent implementations for the Multi-Agent Virtual Company.

This package provides all agent classes:
- BaseAgent: Abstract base class for all agents
- ToolEnabledAgent: Base class for agents with tools
- ResearcherAgent: Web research using Tavily
- AnalystAgent: Data analysis and summarization
- CriticAgent: Quality review (coming soon)
- WriterAgent: Report generation (coming soon)
- SupervisorAgent: Workflow orchestration (coming soon)
"""

from .base import BaseAgent, ToolEnabledAgent, create_llm
from .researcher import ResearcherAgent, create_researcher_agent
from .analyst import AnalystAgent, create_analyst_agent

__all__ = [
    # Base
    "BaseAgent",
    "ToolEnabledAgent",
    "create_llm",
    # Researcher
    "ResearcherAgent",
    "create_researcher_agent",
    # Analyst
    "AnalystAgent",
    "create_analyst_agent",
]
