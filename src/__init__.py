"""
Multi-Agent Virtual Company - Source Package.

A multi-agent AI research system using LangGraph for orchestration.

Components:
- agents: Agent implementations (Researcher, Analyst, Critic, Writer, Supervisor)
- graph: LangGraph workflow (state, nodes, edges, workflow)
- prompts: System prompts for each agent
- schemas: Pydantic models for data validation
- tools: Utility tools (search, scraper, analysis)

Usage:
    from src.graph import create_runner
    
    runner = create_runner(api_key="your-api-key")
    result = runner.run("Your research query")
"""

__version__ = "0.1.0"
__author__ = "Multi-Agent Virtual Company"

# Expose key components at package level
from src.graph import (
    GraphState,
    create_runner,
    create_workflow,
    WorkflowRunner,
    create_initial_state,
)

__all__ = [
    "__version__",
    "GraphState",
    "create_runner",
    "create_workflow",
    "WorkflowRunner",
    "create_initial_state",
]
