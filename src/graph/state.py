"""
LangGraph State Definition for the Multi-Agent Virtual Company.

This module defines the shared state that flows through the graph,
enabling communication between all agents in the workflow.
"""

from typing import Annotated, Optional, Literal
from typing_extensions import TypedDict
from datetime import datetime
from langgraph.graph.message import add_messages

from src.schemas.models import (
    ResearchData,
    AnalysisSummary,
    CritiqueResult,
    FinalReport,
    AgentMessage,
)


# =============================================================================
# Agent Type Definitions
# =============================================================================

AgentType = Literal["supervisor", "researcher", "analyst", "critic", "writer"]
WorkflowStatus = Literal["in_progress", "completed", "failed", "waiting_for_human"]


# =============================================================================
# Custom Reducers for State Updates
# =============================================================================

def update_messages(
    current: list[AgentMessage], 
    new: list[AgentMessage]
) -> list[AgentMessage]:
    """
    Reducer to append new messages to the message history.
    This allows tracking of all agent communications.
    """
    if current is None:
        current = []
    return current + new


def update_iteration_count(current: int, new: int) -> int:
    """
    Reducer to update iteration count.
    Takes the maximum to handle parallel updates.
    """
    return max(current or 0, new or 0)


# =============================================================================
# Graph State Definition
# =============================================================================

class GraphState(TypedDict, total=False):
    """
    Shared state for the multi-agent workflow graph.
    
    This state is passed between all nodes (agents) in the LangGraph workflow.
    Each agent can read from and write to specific parts of the state.
    
    Attributes:
        # User Input
        user_query: The original user query/topic to research
        
        # Workflow Control
        current_agent: Which agent should act next
        next_agent: The next agent to route to (set by supervisor)
        workflow_status: Current status of the workflow
        iteration_count: Number of times through the feedback loop
        max_iterations: Maximum allowed iterations
        
        # Agent Outputs
        research_data: Output from the Researcher agent
        analysis_summary: Output from the Analyst agent
        critique_result: Output from the Critic agent
        final_report: Output from the Writer agent
        
        # Communication
        messages: List of messages between agents (with reducer for appending)
        
        # Error Handling
        error: Any error that occurred
        error_agent: Which agent encountered the error
        
        # Metadata
        started_at: When the workflow started
        completed_at: When the workflow completed
    """
    
    # =========================================================================
    # User Input
    # =========================================================================
    user_query: str
    
    # =========================================================================
    # Workflow Control
    # =========================================================================
    current_agent: AgentType
    next_agent: Optional[AgentType]
    workflow_status: WorkflowStatus
    iteration_count: Annotated[int, update_iteration_count]
    max_iterations: int
    
    # =========================================================================
    # Agent Outputs - Each agent writes to their specific field
    # =========================================================================
    research_data: Optional[ResearchData]
    analysis_summary: Optional[AnalysisSummary]
    critique_result: Optional[CritiqueResult]
    final_report: Optional[FinalReport]
    
    # =========================================================================
    # Communication History
    # =========================================================================
    messages: Annotated[list[AgentMessage], update_messages]
    
    # =========================================================================
    # Error Handling
    # =========================================================================
    error: Optional[str]
    error_agent: Optional[AgentType]
    
    # =========================================================================
    # Metadata
    # =========================================================================
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


# =============================================================================
# State Factory Functions
# =============================================================================

def create_initial_state(user_query: str, max_iterations: int = 3) -> GraphState:
    """
    Create the initial state for a new workflow run.
    
    Args:
        user_query: The user's research query/topic
        max_iterations: Maximum feedback loop iterations (default: 3)
    
    Returns:
        Initial GraphState ready for the workflow
    """
    return GraphState(
        # User input
        user_query=user_query,
        
        # Workflow control
        current_agent="supervisor",
        next_agent=None,
        workflow_status="in_progress",
        iteration_count=0,
        max_iterations=max_iterations,
        
        # Agent outputs (all start as None)
        research_data=None,
        analysis_summary=None,
        critique_result=None,
        final_report=None,
        
        # Communication
        messages=[],
        
        # Error handling
        error=None,
        error_agent=None,
        
        # Metadata
        started_at=datetime.now(),
        completed_at=None,
    )


def get_state_summary(state: GraphState) -> dict:
    """
    Get a summary of the current state for logging/debugging.
    
    Args:
        state: Current graph state
        
    Returns:
        Dictionary with state summary
    """
    return {
        "query": state.get("user_query", "N/A"),
        "status": state.get("workflow_status", "N/A"),
        "current_agent": state.get("current_agent", "N/A"),
        "iteration": state.get("iteration_count", 0),
        "has_research": state.get("research_data") is not None,
        "has_analysis": state.get("analysis_summary") is not None,
        "has_critique": state.get("critique_result") is not None,
        "has_report": state.get("final_report") is not None,
        "message_count": len(state.get("messages", [])),
        "error": state.get("error"),
    }


# =============================================================================
# State Validation
# =============================================================================

def validate_state_transition(
    state: GraphState, 
    from_agent: AgentType, 
    to_agent: AgentType
) -> bool:
    """
    Validate if a state transition is allowed.
    
    Valid transitions:
    - supervisor -> researcher, analyst, critic, writer
    - researcher -> supervisor (with research_data)
    - analyst -> supervisor (with analysis_summary)
    - critic -> supervisor (with critique_result)
    - writer -> supervisor (with final_report)
    
    Args:
        state: Current graph state
        from_agent: Agent transitioning from
        to_agent: Agent transitioning to
        
    Returns:
        True if transition is valid, False otherwise
    """
    # Supervisor can route to any agent
    if from_agent == "supervisor":
        return to_agent in ["researcher", "analyst", "critic", "writer"]
    
    # All other agents must route back to supervisor
    if to_agent != "supervisor":
        return False
    
    # Check that agent has produced required output
    if from_agent == "researcher":
        return state.get("research_data") is not None
    elif from_agent == "analyst":
        return state.get("analysis_summary") is not None
    elif from_agent == "critic":
        return state.get("critique_result") is not None
    elif from_agent == "writer":
        return state.get("final_report") is not None
    
    return False


# Export
__all__ = [
    "GraphState",
    "AgentType",
    "WorkflowStatus",
    "create_initial_state",
    "get_state_summary",
    "validate_state_transition",
]
