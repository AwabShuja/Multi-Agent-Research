"""
Integration tests for the Multi-Agent Virtual Company workflow.

These tests verify the complete workflow functions correctly
from start to finish.
"""

import os
import sys
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    with patch.dict(os.environ, {
        "GROQ_API_KEY": "test-groq-key",
        "TAVILY_API_KEY": "test-tavily-key",
    }):
        yield


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response."""
    mock = MagicMock()
    mock.content = '{"summary": "Test summary", "key_insights": []}'
    return mock


# =============================================================================
# State Tests
# =============================================================================

class TestGraphState:
    """Tests for GraphState and related utilities."""
    
    def test_create_initial_state(self, mock_settings):
        """Test initial state creation."""
        from src.graph.state import create_initial_state
        
        state = create_initial_state("Test query", max_iterations=3)
        
        assert state["user_query"] == "Test query"
        assert state["current_agent"] == "supervisor"
        assert state["workflow_status"] == "in_progress"
        assert state["max_iterations"] == 3
        assert state["iteration_count"] == 0
        assert state["research_data"] is None
        assert state["analysis_summary"] is None
        assert state["critique_result"] is None
        assert state["final_report"] is None
    
    def test_get_state_summary(self, mock_settings):
        """Test state summary generation."""
        from src.graph.state import create_initial_state, get_state_summary
        
        state = create_initial_state("Test query")
        summary = get_state_summary(state)
        
        assert summary["query"] == "Test query"
        assert summary["status"] == "in_progress"
        assert summary["current_agent"] == "supervisor"
        assert summary["iteration"] == 0
        assert summary["has_research"] is False
        assert summary["has_analysis"] is False
        assert summary["has_critique"] is False
        assert summary["has_report"] is False
    
    def test_validate_state_transition(self, mock_settings):
        """Test state transition validation."""
        from src.graph.state import create_initial_state, validate_state_transition
        
        state = create_initial_state("Test query")
        
        # Supervisor can route to any worker
        assert validate_state_transition(state, "supervisor", "researcher") is True
        assert validate_state_transition(state, "supervisor", "analyst") is True
        
        # Workers cannot route to each other directly
        assert validate_state_transition(state, "researcher", "analyst") is False


# =============================================================================
# Node Tests
# =============================================================================

class TestNodes:
    """Tests for workflow nodes."""
    
    def test_node_mapping_exists(self, mock_settings):
        """Test that all required nodes are mapped."""
        from src.graph.nodes import NODE_MAPPING
        
        required_nodes = ["supervisor", "researcher", "analyst", "critic", "writer", "end"]
        
        for node in required_nodes:
            assert node in NODE_MAPPING, f"Missing node: {node}"
    
    def test_agent_registry_singleton(self, mock_settings):
        """Test AgentRegistry singleton pattern."""
        from src.graph.nodes import AgentRegistry, initialize_registry
        
        # Reset any existing instance
        AgentRegistry.reset()
        
        # Initialize
        registry1 = initialize_registry("test-key")
        registry2 = AgentRegistry.get_instance()
        
        assert registry1 is registry2
        
        # Clean up
        AgentRegistry.reset()


# =============================================================================
# Edge Tests
# =============================================================================

class TestEdges:
    """Tests for workflow edges."""
    
    def test_route_from_supervisor_to_researcher(self, mock_settings):
        """Test routing from supervisor to researcher."""
        from src.graph.edges import route_from_supervisor
        from src.graph.state import create_initial_state
        
        state = create_initial_state("Test query")
        state["next_agent"] = "researcher"
        
        result = route_from_supervisor(state)
        assert result == "researcher"
    
    def test_route_from_supervisor_to_end(self, mock_settings):
        """Test routing from supervisor to end."""
        from src.graph.edges import route_from_supervisor
        from src.graph.state import create_initial_state
        
        state = create_initial_state("Test query")
        state["next_agent"] = "END"
        
        result = route_from_supervisor(state)
        assert result == "end"
    
    def test_route_on_error(self, mock_settings):
        """Test error routing."""
        from src.graph.edges import route_from_supervisor
        from src.graph.state import create_initial_state
        
        state = create_initial_state("Test query")
        state["error"] = "Test error"
        
        result = route_from_supervisor(state)
        assert result == "error"
    
    def test_should_revise_analysis(self, mock_settings):
        """Test revision decision logic."""
        from src.graph.edges import should_revise_analysis
        from src.graph.state import create_initial_state
        from src.schemas.models import CritiqueResult
        
        state = create_initial_state("Test query")
        
        # Test with approved critique
        state["critique_result"] = CritiqueResult(
            is_approved=True,
            quality_score=0.85,
            strengths=["Good work"],
            weaknesses=[],
            missing_elements=[],
            suggestions=[],
            revision_required=False,
        )
        
        result = should_revise_analysis(state)
        assert result == "proceed"
        
        # Test with rejected critique
        state["critique_result"] = CritiqueResult(
            is_approved=False,
            quality_score=0.5,
            strengths=[],
            weaknesses=["Needs improvement"],
            missing_elements=["Issue 1"],
            suggestions=["Suggestion 1"],
            revision_required=True,
        )
        
        result = should_revise_analysis(state)
        assert result == "revise"


# =============================================================================
# Workflow Tests
# =============================================================================

class TestWorkflow:
    """Tests for workflow builder and compilation."""
    
    def test_workflow_builder_initialization(self, mock_settings):
        """Test WorkflowBuilder initialization."""
        from src.graph.workflow import WorkflowBuilder
        from src.graph.nodes import AgentRegistry
        
        AgentRegistry.reset()
        
        builder = WorkflowBuilder("test-key")
        
        assert builder.api_key == "test-key"
        assert builder.graph is None
        
        AgentRegistry.reset()
    
    def test_workflow_builds_successfully(self, mock_settings):
        """Test that workflow builds without errors."""
        from src.graph.workflow import WorkflowBuilder
        from src.graph.nodes import AgentRegistry
        
        AgentRegistry.reset()
        
        builder = WorkflowBuilder("test-key")
        graph = builder.build()
        
        assert graph is not None
        
        AgentRegistry.reset()
    
    def test_workflow_compiles_successfully(self, mock_settings):
        """Test that workflow compiles without errors."""
        from src.graph.workflow import WorkflowBuilder
        from src.graph.nodes import AgentRegistry
        
        AgentRegistry.reset()
        
        builder = WorkflowBuilder("test-key")
        builder.build()
        compiled = builder.compile()
        
        assert compiled is not None
        
        # Check that all expected nodes exist
        graph_obj = compiled.get_graph()
        node_names = list(graph_obj.nodes.keys())
        
        assert "supervisor" in node_names
        assert "researcher" in node_names
        assert "analyst" in node_names
        assert "critic" in node_names
        assert "writer" in node_names
        
        AgentRegistry.reset()


# =============================================================================
# Schema Tests
# =============================================================================

class TestSchemas:
    """Tests for Pydantic schemas."""
    
    def test_research_data_creation(self):
        """Test ResearchData model."""
        from src.schemas.models import ResearchData, SearchResult
        
        data = ResearchData(
            topic="Test query",
            search_results=[
                SearchResult(
                    title="Test Source",
                    url="https://example.com",
                    content="Test content",
                    score=0.9,
                )
            ],
            raw_content="Raw content here",
            sources_count=1,
        )
        
        assert data.topic == "Test query"
        assert len(data.search_results) == 1
        assert data.search_results[0].title == "Test Source"
    
    def test_analysis_summary_creation(self):
        """Test AnalysisSummary model."""
        from src.schemas.models import AnalysisSummary, KeyInsight
        
        summary = AnalysisSummary(
            topic="Test topic",
            executive_summary="Main findings here",
            key_insights=[
                KeyInsight(
                    insight="Test insight",
                    confidence="high",
                    supporting_sources=["Test source"],
                )
            ],
            sentiment="neutral",
            data_quality_score=0.8,
        )
        
        assert summary.executive_summary == "Main findings here"
        assert len(summary.key_insights) == 1
        assert summary.data_quality_score == 0.8
    
    def test_critique_result_creation(self):
        """Test CritiqueResult model."""
        from src.schemas.models import CritiqueResult
        
        critique = CritiqueResult(
            is_approved=True,
            quality_score=0.85,
            strengths=["Good analysis"],
            weaknesses=[],
            missing_elements=[],
            suggestions=["Minor suggestion"],
            revision_required=False,
        )
        
        assert critique.is_approved is True
        assert critique.quality_score == 0.85
    
    def test_final_report_creation(self):
        """Test FinalReport model."""
        from src.schemas.models import FinalReport, ReportSection
        
        report = FinalReport(
            title="Test Report",
            topic="Test topic",
            executive_summary="Executive summary here",
            sections=[
                ReportSection(
                    title="Introduction",
                    content="Introduction content",
                )
            ],
            key_takeaways=["Key takeaway 1"],
            recommendations=["Recommendation 1"],
            sources=["https://example.com"],
        )
        
        assert report.title == "Test Report"
        assert len(report.sections) == 1


# =============================================================================
# Agent Tests
# =============================================================================

class TestAgents:
    """Tests for agent classes."""
    
    def test_all_agents_importable(self, mock_settings):
        """Test that all agents can be imported."""
        from src.agents import (
            BaseAgent,
            ResearcherAgent,
            AnalystAgent,
            CriticAgent,
            WriterAgent,
            SupervisorAgent,
        )
        
        # Just verify imports work
        assert BaseAgent is not None
        assert ResearcherAgent is not None
        assert AnalystAgent is not None
        assert CriticAgent is not None
        assert WriterAgent is not None
        assert SupervisorAgent is not None
    
    def test_agent_factory_functions(self, mock_settings):
        """Test agent factory functions."""
        from src.agents import (
            create_researcher_agent,
            create_analyst_agent,
            create_critic_agent,
            create_writer_agent,
            create_supervisor_agent,
        )
        
        # Just verify factories exist
        assert callable(create_researcher_agent)
        assert callable(create_analyst_agent)
        assert callable(create_critic_agent)
        assert callable(create_writer_agent)
        assert callable(create_supervisor_agent)


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
