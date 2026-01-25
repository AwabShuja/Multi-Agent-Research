"""
Test configuration and fixtures for pytest.
"""

import os
import sys
from pathlib import Path

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment with mock API keys."""
    os.environ["GROQ_API_KEY"] = "test-groq-api-key-12345"
    os.environ["TAVILY_API_KEY"] = "test-tavily-api-key-12345"
    yield
    # Cleanup if needed


@pytest.fixture
def sample_query():
    """Sample research query for testing."""
    return "What are the latest trends in artificial intelligence?"


@pytest.fixture
def sample_research_data():
    """Sample research data for testing."""
    from src.schemas.models import ResearchData, SearchResult
    
    return ResearchData(
        topic="AI trends",
        search_results=[
            SearchResult(
                title="AI in 2025",
                url="https://example.com/ai-2025",
                content="AI is advancing rapidly with new developments in LLMs...",
                score=0.95,
            ),
            SearchResult(
                title="Machine Learning Trends",
                url="https://example.com/ml-trends",
                content="Machine learning continues to evolve with new architectures...",
                score=0.88,
            ),
        ],
        raw_content="Combined content from all sources...",
        sources_count=2,
    )


@pytest.fixture
def sample_analysis():
    """Sample analysis summary for testing."""
    from src.schemas.models import AnalysisSummary, KeyInsight
    
    return AnalysisSummary(
        topic="AI trends",
        executive_summary="AI is experiencing rapid growth in 2025...",
        key_insights=[
            KeyInsight(
                insight="LLMs are becoming more efficient",
                confidence="high",
                supporting_sources=["https://example.com/ai-2025"],
            ),
            KeyInsight(
                insight="Multi-agent systems are gaining traction",
                confidence="high",
                supporting_sources=["https://example.com/ml-trends"],
            ),
        ],
        sentiment="bullish",
        data_quality_score=0.85,
    )


@pytest.fixture
def sample_critique_approved():
    """Sample approved critique for testing."""
    from src.schemas.models import CritiqueResult
    
    return CritiqueResult(
        is_approved=True,
        quality_score=0.82,
        strengths=["Comprehensive coverage", "Good source diversity"],
        weaknesses=[],
        missing_elements=[],
        suggestions=["Consider adding more recent sources"],
        revision_required=False,
    )


@pytest.fixture
def sample_critique_rejected():
    """Sample rejected critique for testing."""
    from src.schemas.models import CritiqueResult
    
    return CritiqueResult(
        is_approved=False,
        quality_score=0.55,
        strengths=[],
        weaknesses=["The analysis needs more depth and supporting evidence"],
        missing_elements=[
            "Insufficient source coverage",
            "Missing quantitative data",
        ],
        suggestions=[
            "Add more diverse sources",
            "Include statistical evidence",
            "Expand on key points",
        ],
        revision_required=True,
    )


@pytest.fixture
def sample_final_report():
    """Sample final report for testing."""
    from src.schemas.models import FinalReport, ReportSection
    
    return FinalReport(
        title="AI Trends Analysis Report 2025",
        topic="AI trends",
        executive_summary="This report examines the current state of AI...",
        sections=[
            ReportSection(
                title="Introduction",
                content="Artificial intelligence continues to evolve...",
            ),
            ReportSection(
                title="Key Findings",
                content="Our analysis reveals several important trends...",
            ),
            ReportSection(
                title="Recommendations",
                content="Based on our findings, we recommend...",
            ),
        ],
        key_takeaways=["AI will continue to transform industries"],
        recommendations=["Invest in AI capabilities"],
        sources=[
            "https://example.com/ai-2025",
            "https://example.com/ml-trends",
        ],
    )
