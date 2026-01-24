"""
LangGraph workflow and state management.

This package provides:
- State: GraphState definition and utilities
- Nodes: Agent node functions
- Edges: Conditional routing logic
- Workflow: StateGraph builder and runner
"""

from .state import (
    GraphState,
    AgentType,
    WorkflowStatus,
    create_initial_state,
    get_state_summary,
    validate_state_transition,
)
from .nodes import (
    AgentRegistry,
    initialize_registry,
    get_registry,
    supervisor_node,
    researcher_node,
    analyst_node,
    critic_node,
    writer_node,
    end_node,
    NODE_MAPPING,
    get_node_function,
)
from .edges import (
    route_from_supervisor,
    route_after_researcher,
    route_after_analyst,
    route_after_critic,
    route_after_writer,
    should_continue_workflow,
    should_revise_analysis,
    route_on_error,
    EdgeConfig,
)
from .workflow import (
    WorkflowBuilder,
    WorkflowRunner,
    create_workflow,
    create_runner,
    get_workflow_diagram,
)

__all__ = [
    # State
    "GraphState",
    "AgentType",
    "WorkflowStatus",
    "create_initial_state",
    "get_state_summary",
    "validate_state_transition",
    # Nodes
    "AgentRegistry",
    "initialize_registry",
    "get_registry",
    "supervisor_node",
    "researcher_node",
    "analyst_node",
    "critic_node",
    "writer_node",
    "end_node",
    "NODE_MAPPING",
    "get_node_function",
    # Edges
    "route_from_supervisor",
    "route_after_researcher",
    "route_after_analyst",
    "route_after_critic",
    "route_after_writer",
    "should_continue_workflow",
    "should_revise_analysis",
    "route_on_error",
    "EdgeConfig",
    # Workflow
    "WorkflowBuilder",
    "WorkflowRunner",
    "create_workflow",
    "create_runner",
    "get_workflow_diagram",
]
