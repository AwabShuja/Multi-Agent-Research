"""
Multi-Agent Virtual Company - Streamlit Interface.

A clean, user-friendly interface for running AI-powered research
through the multi-agent workflow system.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import time

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Custom CSS for clean UI
# =============================================================================

st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 1rem 2rem;
    }
    
    /* Header styling */
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    /* Agent status cards */
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .agent-card-inactive {
        background: #f3f4f6;
        border-radius: 12px;
        padding: 1rem;
        color: #9ca3af;
        margin-bottom: 0.5rem;
    }
    
    .agent-card-complete {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    /* Status indicator */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .status-running {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .status-complete {
        background-color: #d1fae5;
        color: #065f46;
    }
    
    .status-error {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    /* Report section */
    .report-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Improve button styling */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Session State Initialization
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if "workflow_running" not in st.session_state:
        st.session_state.workflow_running = False
    if "current_agent" not in st.session_state:
        st.session_state.current_agent = None
    if "workflow_result" not in st.session_state:
        st.session_state.workflow_result = None
    if "error" not in st.session_state:
        st.session_state.error = None
    if "agent_status" not in st.session_state:
        st.session_state.agent_status = {
            "researcher": "pending",
            "analyst": "pending",
            "critic": "pending",
            "writer": "pending",
        }


# =============================================================================
# Sidebar
# =============================================================================

def render_sidebar():
    """Render the sidebar with settings and info."""
    with st.sidebar:
        st.markdown("## Settings")
        
        max_iterations = st.slider(
            "Max Revision Iterations",
            min_value=1,
            max_value=5,
            value=3,
            help="Maximum times the Critic can request revisions",
        )
        
        st.markdown("---")
        
        st.markdown("## Agent Workflow")
        st.markdown("""
        1. **Researcher** - Gathers information from the web
        2. **Analyst** - Analyzes and summarizes findings
        3. **Critic** - Reviews quality and may request revisions
        4. **Writer** - Creates the final polished report
        """)
        
        st.markdown("---")
        
        st.markdown("## About")
        st.markdown("""
        This AI Research Assistant uses multiple specialized agents 
        to research topics and generate comprehensive reports.
        
        Built with LangGraph and Groq's LLM API.
        """)
        
        return max_iterations


# =============================================================================
# Agent Status Display
# =============================================================================

def render_agent_status():
    """Render the agent status indicators."""
    agents = [
        ("researcher", "Researcher", "Gathering web sources"),
        ("analyst", "Analyst", "Analyzing data"),
        ("critic", "Critic", "Reviewing quality"),
        ("writer", "Writer", "Creating report"),
    ]
    
    cols = st.columns(4)
    
    for i, (agent_id, name, description) in enumerate(agents):
        with cols[i]:
            status = st.session_state.agent_status.get(agent_id, "pending")
            
            if status == "running":
                st.markdown(f"""
                <div class="agent-card">
                    <div style="font-weight: 600; font-size: 1rem;">⚡ {name}</div>
                    <div style="font-size: 0.8rem; opacity: 0.9;">{description}</div>
                </div>
                """, unsafe_allow_html=True)
            elif status == "complete":
                st.markdown(f"""
                <div class="agent-card-complete">
                    <div style="font-weight: 600; font-size: 1rem;">✓ {name}</div>
                    <div style="font-size: 0.8rem; opacity: 0.9;">Complete</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="agent-card-inactive">
                    <div style="font-weight: 600; font-size: 1rem;">{name}</div>
                    <div style="font-size: 0.8rem;">{description}</div>
                </div>
                """, unsafe_allow_html=True)


# =============================================================================
# Workflow Execution
# =============================================================================

def run_workflow(query: str, max_iterations: int):
    """Run the multi-agent workflow."""
    try:
        from config.settings import settings
        from src.graph import create_runner, get_state_summary
        
        if settings is None:
            st.error("Configuration error. Please check your .env file has valid API keys.")
            return None
        
        # Create runner
        runner = create_runner(
            api_key=settings.groq_api_key,
            tavily_api_key=settings.tavily_api_key,
            max_iterations=max_iterations,
            enable_checkpointing=False,
        )
        
        # Run workflow
        result = runner.run(query)
        
        return result
        
    except Exception as e:
        st.session_state.error = str(e)
        return None


def run_workflow_with_progress(query: str, max_iterations: int, progress_placeholder, status_placeholder):
    """Run workflow with progress updates."""
    try:
        from config.settings import settings
        from src.graph import WorkflowRunner, get_state_summary
        from src.graph.nodes import AgentRegistry
        
        if settings is None:
            st.error("Configuration error. Please check your .env file.")
            return None
        
        # Reset registry for fresh run
        AgentRegistry.reset()
        
        # Update status
        status_placeholder.info("Initializing workflow...")
        progress_placeholder.progress(0.1)
        
        # Create runner
        runner = WorkflowRunner(
            api_key=settings.groq_api_key,
            tavily_api_key=settings.tavily_api_key,
            max_iterations=max_iterations,
            enable_checkpointing=False,
        )
        
        # Update progress for researcher
        st.session_state.agent_status["researcher"] = "running"
        status_placeholder.info("🔍 Researcher is gathering information...")
        progress_placeholder.progress(0.25)
        
        # Run workflow (this runs all agents)
        result = runner.run(query)
        
        # Update all agents to complete
        for agent in ["researcher", "analyst", "critic", "writer"]:
            st.session_state.agent_status[agent] = "complete"
        
        progress_placeholder.progress(1.0)
        
        if result.get("error"):
            status_placeholder.error(f"Workflow error: {result['error']}")
        else:
            status_placeholder.success("Research completed successfully!")
        
        return result
        
    except Exception as e:
        status_placeholder.error(f"Error: {str(e)}")
        st.session_state.error = str(e)
        return None


# =============================================================================
# Report Display
# =============================================================================

def render_report(result: dict):
    """Render the final report."""
    if not result:
        return
    
    final_report = result.get("final_report")
    
    if not final_report:
        st.warning("No report was generated. Check the workflow logs for details.")
        return
    
    # Report header
    st.markdown("---")
    st.markdown("## 📄 Research Report")
    
    # Title
    if hasattr(final_report, "title"):
        st.markdown(f"### {final_report.title}")
    
    # Executive Summary
    if hasattr(final_report, "executive_summary"):
        with st.expander("📋 Executive Summary", expanded=True):
            st.markdown(final_report.executive_summary)
    
    # Main Sections
    if hasattr(final_report, "sections") and final_report.sections:
        for section in final_report.sections:
            with st.expander(f"📑 {section.title}", expanded=False):
                st.markdown(section.content)
    
    # Key Takeaways
    if hasattr(final_report, "key_takeaways") and final_report.key_takeaways:
        with st.expander("🎯 Key Takeaways", expanded=True):
            for takeaway in final_report.key_takeaways:
                st.markdown(f"• {takeaway}")
    
    # Recommendations
    if hasattr(final_report, "recommendations") and final_report.recommendations:
        with st.expander("💡 Recommendations", expanded=False):
            for i, rec in enumerate(final_report.recommendations, 1):
                st.markdown(f"{i}. {rec}")
    
    # Sources
    if hasattr(final_report, "sources") and final_report.sources:
        with st.expander("🔗 Sources", expanded=False):
            for source in final_report.sources:
                st.markdown(f"• {source}")
    
    # Download button
    st.markdown("---")
    if hasattr(final_report, "to_markdown"):
        markdown_content = final_report.to_markdown()
        st.download_button(
            label="📥 Download Report (Markdown)",
            data=markdown_content,
            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
        )


def render_debug_info(result: dict):
    """Render debug information about the workflow."""
    if not result:
        return
    
    with st.expander("🔧 Workflow Details", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", result.get("workflow_status", "Unknown"))
        with col2:
            st.metric("Iterations", result.get("iteration_count", 0))
        with col3:
            has_report = "Yes" if result.get("final_report") else "No"
            st.metric("Report Generated", has_report)
        
        if result.get("error"):
            st.error(f"Error: {result['error']}")
        
        # Show critique result if available
        if result.get("critique_result"):
            critique = result["critique_result"]
            st.markdown("**Critique Result:**")
            if hasattr(critique, "quality_score"):
                st.progress(critique.quality_score, text=f"Quality Score: {critique.quality_score:.0%}")
            if hasattr(critique, "is_approved"):
                st.write(f"Approved: {'Yes' if critique.is_approved else 'No'}")


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    # Header
    st.markdown('<p class="header-title">🔬 AI Research Assistant</p>', unsafe_allow_html=True)
    st.markdown('<p class="header-subtitle">Multi-agent powered research and report generation</p>', unsafe_allow_html=True)
    
    # Sidebar
    max_iterations = render_sidebar()
    
    # Main input area
    st.markdown("### What would you like to research?")
    
    query = st.text_area(
        "Enter your research topic or question",
        placeholder="Example: What are the latest developments in AI agents and their applications in enterprise?",
        height=100,
        label_visibility="collapsed",
    )
    
    # Start button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_button = st.button(
            "🚀 Start Research",
            type="primary",
            disabled=st.session_state.workflow_running or not query.strip(),
            use_container_width=True,
        )
    
    # Agent status display
    st.markdown("---")
    st.markdown("### Agent Status")
    render_agent_status()
    
    # Progress and status placeholders
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Run workflow
    if start_button and query.strip():
        # Reset state
        st.session_state.workflow_running = True
        st.session_state.workflow_result = None
        st.session_state.error = None
        st.session_state.agent_status = {
            "researcher": "pending",
            "analyst": "pending",
            "critic": "pending",
            "writer": "pending",
        }
        
        # Run with progress
        result = run_workflow_with_progress(
            query.strip(),
            max_iterations,
            progress_placeholder,
            status_placeholder,
        )
        
        st.session_state.workflow_result = result
        st.session_state.workflow_running = False
        
        # Rerun to update UI
        st.rerun()
    
    # Display results
    if st.session_state.workflow_result:
        render_report(st.session_state.workflow_result)
        render_debug_info(st.session_state.workflow_result)
    
    # Error display
    if st.session_state.error:
        st.error(f"An error occurred: {st.session_state.error}")


if __name__ == "__main__":
    main()
