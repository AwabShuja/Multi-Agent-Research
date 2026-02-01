"""
Multi-Agent Virtual Company - Enhanced Interactive Streamlit Interface.

A modern, animated, and user-friendly interface for running AI-powered research
through the multi-agent workflow system with advanced UI/UX features.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import time
import json

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="AI Research Assistant Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# Enhanced CSS with Animations and Modern Design
# =============================================================================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInFromLeft {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes shimmer {
        0% { background-position: -468px 0; }
        100% { background-position: 468px 0; }
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-10px); }
        60% { transform: translateY(-5px); }
    }
    
    /* Main container with glassmorphism */
    .main {
        padding: 1rem 2rem;
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glass container for content */
    .glass-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Header styling with animation */
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        animation: slideInFromLeft 1s ease-out;
        text-align: center;
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 2rem;
        text-align: center;
        animation: fadeIn 1.2s ease-out;
    }
    
    /* Enhanced agent status cards with hover effects */
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        transform: translateY(0);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        animation: fadeIn 0.6s ease-out;
    }
    
    .agent-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .agent-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .agent-card:hover::before {
        left: 100%;
    }
    
    .agent-card-running {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(240, 147, 251, 0.4);
        animation: pulse 2s infinite, fadeIn 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .agent-card-running::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(-45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        animation: shimmer 2s infinite;
    }
    
    .agent-card-inactive {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        color: rgba(255, 255, 255, 0.6);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        animation: fadeIn 0.6s ease-out;
    }
    
    .agent-card-complete {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
        animation: bounce 0.8s ease-out, fadeIn 0.6s ease-out;
        position: relative;
    }
    
    .agent-card-complete::before {
        content: '✓';
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 1.5rem;
        animation: bounce 1s ease-out 0.5s;
    }
    
    /* Enhanced progress bar */
    .progress-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50px;
        padding: 4px;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .progress-bar {
        height: 12px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        border-radius: 50px;
        transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 2s infinite;
    }
    
    /* Interactive buttons with hover effects */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* Input field styling */
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(102, 126, 234, 0.8) !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Status indicators with animations */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.25rem;
        animation: fadeIn 0.5s ease-out;
        transition: all 0.3s ease;
    }
    
    .status-running {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        animation: pulse 2s infinite;
    }
    
    .status-complete {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        animation: bounce 0.8s ease-out;
    }
    
    /* Report section enhancements */
    .report-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        animation: fadeIn 1s ease-out;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255, 255, 255, 0.15) !important;
        transform: translateY(-1px);
    }
    
    /* Metrics styling */
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        animation: fadeIn 0.8s ease-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 3px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        border-top: 3px solid #667eea;
        width: 30px;
        height: 30px;
        animation: rotate 1s linear infinite;
        margin: 0 auto;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.6);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.8);
    }
    
    /* Notification styles */
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        animation: slideInFromRight 0.5s ease-out;
        z-index: 1000;
    }
    
    @keyframes slideInFromRight {
        from { transform: translateX(100px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Enhanced Session State with Animation Tracking
# =============================================================================

def init_session_state():
    """Initialize session state variables with animation tracking."""
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
    if "progress_value" not in st.session_state:
        st.session_state.progress_value = 0
    if "last_status_update" not in st.session_state:
        st.session_state.last_status_update = ""
    if "workflow_start_time" not in st.session_state:
        st.session_state.workflow_start_time = None
    if "agent_completion_times" not in st.session_state:
        st.session_state.agent_completion_times = {}


# =============================================================================
# Interactive Sidebar with Enhanced Features  
# =============================================================================

def render_enhanced_sidebar():
    """Render the enhanced animated sidebar."""
    with st.sidebar:
        # Animated header
        st.markdown("""
        <div style="text-align: center; animation: fadeIn 1s ease-out;">
            <h1 style="font-size: 1.8rem; margin-bottom: 0;">⚙️</h1>
            <h2 style="color: rgba(255,255,255,0.9); font-size: 1.4rem;">Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Enhanced settings with tooltips
        max_iterations = st.slider(
            "🔄 Max Revision Iterations",
            min_value=1,
            max_value=5,
            value=3,
            help="Maximum times the Critic can request revisions for quality improvement",
        )
        
        # Model selection
        st.markdown("#### 🤖 AI Model Settings")
        model_temp = st.slider(
            "Temperature (Creativity)",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more creative but less focused"
        )
        
        # Search settings
        st.markdown("#### 🔍 Search Configuration")
        max_search_results = st.slider(
            "Max Search Results", 
            min_value=3,
            max_value=10,
            value=5,
            help="Number of sources to gather per search query"
        )
        
        st.markdown("---")
        
        # Animated workflow visualization
        st.markdown("""
        <div style="animation: slideInFromLeft 1s ease-out;">
            <h3 style="color: rgba(255,255,255,0.9);">🔄 Workflow Pipeline</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive workflow steps
        workflow_steps = [
            ("🔍", "Researcher", "Gathers comprehensive information", "primary"),
            ("📊", "Analyst", "Analyzes and synthesizes data", "secondary"), 
            ("⚖️", "Critic", "Reviews quality and accuracy", "warning"),
            ("✍️", "Writer", "Crafts the final report", "success"),
        ]
        
        for i, (icon, name, desc, color) in enumerate(workflow_steps):
            status = st.session_state.agent_status.get(name.lower(), "pending")
            
            if status == "complete":
                st.success(f"{icon} **{name}** ✓")
            elif status == "running":
                st.info(f"{icon} **{name}** 🔄")
            else:
                st.write(f"{icon} **{name}**")
            
            with st.expander(f"About {name}", expanded=False):
                st.write(desc)
            
            if i < len(workflow_steps) - 1:
                st.markdown("<div style='text-align: center; color: rgba(255,255,255,0.5);'>↓</div>", 
                           unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Performance metrics
        if st.session_state.workflow_start_time:
            elapsed = time.time() - st.session_state.workflow_start_time
            st.markdown("#### ⏱️ Performance")
            st.metric("Elapsed Time", f"{elapsed:.1f}s")
            
            completed_agents = sum(1 for status in st.session_state.agent_status.values() 
                                 if status == "complete")
            st.metric("Agents Completed", f"{completed_agents}/4")
        
        # About section with animation
        st.markdown("---")
        st.markdown("""
        <div style="animation: fadeIn 2s ease-out;">
            <h3 style="color: rgba(255,255,255,0.9);">💡 About</h3>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
                This AI Research Assistant uses advanced multi-agent orchestration
                to research topics and generate comprehensive, high-quality reports.
            </p>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.8rem;">
                Powered by LangGraph, Groq's LLM API, and Tavily Search.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        return max_iterations, model_temp, max_search_results


# =============================================================================
# Interactive Agent Status Display with Animations
# =============================================================================

def render_interactive_agent_status():
    """Render the animated interactive agent status display."""
    agents = [
        ("researcher", "🔍", "Researcher", "Gathering comprehensive web sources"),
        ("analyst", "📊", "Analyst", "Analyzing and synthesizing data"),
        ("critic", "⚖️", "Critic", "Reviewing quality and accuracy"),
        ("writer", "✍️", "Writer", "Crafting polished final report"),
    ]
    
    # Create animated header
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0; animation: fadeIn 1s ease-out;">
        <h2 style="color: rgba(255,255,255,0.9); font-size: 1.8rem; margin-bottom: 0.5rem;">
            🤖 Agent Status Dashboard
        </h2>
        <p style="color: rgba(255,255,255,0.7);">Real-time workflow progress monitoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress overview
    completed_count = sum(1 for agent_id, _, _, _ in agents 
                         if st.session_state.agent_status.get(agent_id) == "complete")
    running_count = sum(1 for agent_id, _, _, _ in agents 
                       if st.session_state.agent_status.get(agent_id) == "running")
    
    # Overall progress bar
    overall_progress = completed_count / len(agents)
    st.markdown(f"""
    <div class="glass-container" style="margin: 1rem 0; padding: 1rem;">
        <h4 style="color: rgba(255,255,255,0.9); margin-bottom: 1rem;">Overall Progress</h4>
        <div class="progress-container">
            <div class="progress-bar" style="width: {overall_progress * 100}%"></div>
        </div>
        <p style="color: rgba(255,255,255,0.7); margin-top: 0.5rem; text-align: center;">
            {completed_count}/{len(agents)} Agents Completed
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Agent cards in grid layout
    cols = st.columns(2)
    
    for i, (agent_id, icon, name, description) in enumerate(agents):
        with cols[i % 2]:
            status = st.session_state.agent_status.get(agent_id, "pending")
            completion_time = st.session_state.agent_completion_times.get(agent_id, "")
            
            if status == "running":
                # Animated running state
                st.markdown(f"""
                <div class="agent-card-running">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.8rem; margin-right: 0.5rem;">{icon}</div>
                        <div>
                            <div style="font-weight: 600; font-size: 1.1rem;">{name}</div>
                            <div style="font-size: 0.9rem; opacity: 0.9;">{description}</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div class="status-badge status-running">
                            🔄 Processing...
                        </div>
                        <div class="loading-spinner"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            elif status == "complete":
                # Animated complete state
                st.markdown(f"""
                <div class="agent-card-complete">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.8rem; margin-right: 0.5rem;">{icon}</div>
                        <div>
                            <div style="font-weight: 600; font-size: 1.1rem;">{name}</div>
                            <div style="font-size: 0.9rem; opacity: 0.9;">Task completed successfully</div>
                        </div>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div class="status-badge status-complete">
                            ✓ Complete
                        </div>
                        {f'<div style="font-size: 0.8rem; opacity: 0.8;">{completion_time}</div>' if completion_time else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                # Pending state with hover effects
                st.markdown(f"""
                <div class="agent-card-inactive">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <div style="font-size: 1.8rem; margin-right: 0.5rem; opacity: 0.6;">{icon}</div>
                        <div>
                            <div style="font-weight: 600; font-size: 1.1rem;">{name}</div>
                            <div style="font-size: 0.9rem;">{description}</div>
                        </div>
                    </div>
                    <div class="status-badge" style="background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6);">
                        ⏳ Pending
                    </div>
                </div>
                """, unsafe_allow_html=True)


# =============================================================================
# Enhanced Progress Tracking with Real-time Updates
# =============================================================================

def create_animated_progress_display():
    """Create an animated progress display with real-time updates."""
    
    # Create containers for dynamic updates
    progress_container = st.empty()
    status_container = st.empty()
    metrics_container = st.empty()
    
    return progress_container, status_container, metrics_container

def update_progress_display(progress_container, status_container, metrics_container, 
                           progress_value, status_message, elapsed_time=None):
    """Update the progress display with animations."""
    
    with progress_container.container():
        st.markdown(f"""
        <div class="glass-container" style="text-align: center;">
            <h3 style="color: rgba(255,255,255,0.9); margin-bottom: 1rem;">Workflow Progress</h3>
            <div class="progress-container" style="margin: 1.5rem 0;">
                <div class="progress-bar" style="width: {progress_value * 100}%"></div>
            </div>
            <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
                {progress_value * 100:.1f}% Complete
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with status_container.container():
        if "error" in status_message.lower():
            badge_class = "status-error"
            icon = "❌"
        elif "complete" in status_message.lower():
            badge_class = "status-complete" 
            icon = "✅"
        else:
            badge_class = "status-running"
            icon = "🔄"
            
        st.markdown(f"""
        <div style="text-align: center; margin: 1rem 0;">
            <div class="status-badge {badge_class}" style="font-size: 1rem; padding: 0.75rem 1.5rem;">
                {icon} {status_message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if elapsed_time and metrics_container:
        with metrics_container.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.2rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                        ⏱️ {elapsed_time:.1f}s
                    </div>
                    <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">Elapsed Time</div>
                </div>
                """, unsafe_allow_html=True)
            
            completed_agents = sum(1 for status in st.session_state.agent_status.values() 
                                 if status == "complete")
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.2rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                        🤖 {completed_agents}/4
                    </div>
                    <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">Agents Complete</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                estimated_remaining = max(0, (elapsed_time / max(1, completed_agents)) * (4 - completed_agents))
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 1.2rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                        📊 {estimated_remaining:.0f}s
                    </div>
                    <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">Est. Remaining</div>
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


def run_enhanced_workflow_with_progress(query: str, max_iterations: int, 
                                       progress_container, status_container, metrics_container):
    """Run workflow with enhanced real-time progress updates and animations."""
    try:
        from config.settings import settings
        from src.graph import WorkflowRunner, get_state_summary
        from src.graph.nodes import AgentRegistry
        
        if settings is None:
            st.error("⚠️ Configuration error. Please check your .env file has valid API keys.")
            return None
        
        # Initialize timing
        st.session_state.workflow_start_time = time.time()
        
        # Reset registry for fresh run
        AgentRegistry.reset()
        
        # Update initial status
        update_progress_display(progress_container, status_container, metrics_container,
                               0.0, "Initializing AI Research Assistant...")
        time.sleep(0.5)  # Allow animation to show
        
        # Create runner with enhanced error handling
        try:
            runner = WorkflowRunner(
                api_key=settings.groq_api_key,
                tavily_api_key=settings.tavily_api_key,
                max_iterations=max_iterations,
                enable_checkpointing=False,
            )
        except Exception as e:
            update_progress_display(progress_container, status_container, metrics_container,
                                   0.0, f"Setup Error: {str(e)}")
            return None
        
        # Phase 1: Research
        st.session_state.agent_status["researcher"] = "running"
        elapsed = time.time() - st.session_state.workflow_start_time
        update_progress_display(progress_container, status_container, metrics_container,
                               0.15, "🔍 Researcher gathering comprehensive information...", elapsed)
        
        # Phase 2: Analysis  
        st.session_state.agent_status["analyst"] = "running"
        elapsed = time.time() - st.session_state.workflow_start_time
        update_progress_display(progress_container, status_container, metrics_container,
                               0.35, "📊 Analyst synthesizing research findings...", elapsed)
        
        # Run the complete workflow
        result = runner.run(query)
        
        # Phase 3: Critique (simulated progress updates)
        st.session_state.agent_status["researcher"] = "complete"
        st.session_state.agent_completion_times["researcher"] = f"Completed in {elapsed:.1f}s"
        st.session_state.agent_status["critic"] = "running"
        elapsed = time.time() - st.session_state.workflow_start_time
        update_progress_display(progress_container, status_container, metrics_container,
                               0.65, "⚖️ Critic reviewing quality and accuracy...", elapsed)
        
        # Phase 4: Writing
        st.session_state.agent_status["analyst"] = "complete"
        st.session_state.agent_completion_times["analyst"] = f"Completed in {elapsed:.1f}s"
        st.session_state.agent_status["writer"] = "running"
        elapsed = time.time() - st.session_state.workflow_start_time
        update_progress_display(progress_container, status_container, metrics_container,
                               0.85, "✍️ Writer crafting polished final report...", elapsed)
        
        # Completion
        for agent in ["researcher", "analyst", "critic", "writer"]:
            st.session_state.agent_status[agent] = "complete"
            if agent not in st.session_state.agent_completion_times:
                st.session_state.agent_completion_times[agent] = f"Completed in {elapsed:.1f}s"
        
        elapsed = time.time() - st.session_state.workflow_start_time
        
        if result.get("error"):
            update_progress_display(progress_container, status_container, metrics_container,
                                   1.0, f"❌ Workflow Error: {result['error']}", elapsed)
        else:
            update_progress_display(progress_container, status_container, metrics_container,
                                   1.0, "✅ Research completed successfully!", elapsed)
            
            # Show success notification
            st.markdown("""
            <div class="notification">
                <div style="color: rgba(255,255,255,0.9); font-weight: 600;">
                    🎉 Research Complete!
                </div>
                <div style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">
                    Your comprehensive report is ready
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        return result
        
    except Exception as e:
        elapsed = time.time() - st.session_state.workflow_start_time if st.session_state.workflow_start_time else 0
        update_progress_display(progress_container, status_container, metrics_container,
                               0.0, f"❌ System Error: {str(e)}", elapsed)
        st.session_state.error = str(e)
        return None


# =============================================================================
# Enhanced Report Display with Interactive Elements
# =============================================================================

def render_enhanced_report(result: dict):
    """Render the final report with enhanced animations and interactivity."""
    if not result:
        return
    
    final_report = result.get("final_report")
    
    if not final_report:
        st.markdown("""
        <div class="glass-container" style="text-align: center;">
            <h3 style="color: rgba(255,255,255,0.9);">⚠️ No Report Generated</h3>
            <p style="color: rgba(255,255,255,0.7);">
                The workflow completed but no report was generated. 
                Please check the workflow logs for details.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Animated report header
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0; animation: fadeIn 1s ease-out;">
        <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   background-clip: text; margin-bottom: 0.5rem;">
            📄 Research Report Generated
        </h1>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
            Comprehensive AI-powered research analysis
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Report metrics
    word_count = len(str(final_report).split()) if final_report else 0
    sections_count = len(final_report.sections) if hasattr(final_report, "sections") and final_report.sections else 0
    sources_count = len(final_report.sources) if hasattr(final_report, "sources") and final_report.sources else 0
    
    # Animated metrics cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="animation: fadeIn 0.8s ease-out 0.2s both;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📝</div>
            <div style="font-size: 1.4rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                {word_count}
            </div>
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">Total Words</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="animation: fadeIn 0.8s ease-out 0.4s both;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">📑</div>
            <div style="font-size: 1.4rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                {sections_count}
            </div>
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">Sections</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="animation: fadeIn 0.8s ease-out 0.6s both;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">🔗</div>
            <div style="font-size: 1.4rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                {sources_count}
            </div>
            <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">Sources</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Report title with animation
    if hasattr(final_report, "title"):
        st.markdown(f"""
        <div class="glass-container" style="animation: slideInFromLeft 1s ease-out;">
            <h2 style="color: rgba(255,255,255,0.9); font-size: 1.8rem; text-align: center; margin: 0;">
                {final_report.title}
            </h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Executive Summary with enhanced styling
    if hasattr(final_report, "executive_summary"):
        with st.expander("📋 Executive Summary", expanded=True):
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; 
                        border-left: 4px solid #667eea; animation: fadeIn 1s ease-out;">
                <div style="color: rgba(255,255,255,0.9); line-height: 1.6; font-size: 1.05rem;">
                    {final_report.executive_summary}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Main Sections with progressive animation
    if hasattr(final_report, "sections") and final_report.sections:
        st.markdown("""
        <h3 style="color: rgba(255,255,255,0.9); margin: 2rem 0 1rem 0;">
            📚 Detailed Analysis
        </h3>
        """, unsafe_allow_html=True)
        
        for i, section in enumerate(final_report.sections):
            with st.expander(f"📑 {section.title}", expanded=False):
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); padding: 1.5rem; border-radius: 12px; 
                            animation: fadeIn 0.8s ease-out {i*0.1}s both;">
                    <div style="color: rgba(255,255,255,0.9); line-height: 1.6;">
                        {section.content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Key Takeaways with bullet animations
    if hasattr(final_report, "key_takeaways") and final_report.key_takeaways:
        with st.expander("🎯 Key Takeaways", expanded=True):
            st.markdown("""
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; 
                        border-left: 4px solid #10b981;">
            """, unsafe_allow_html=True)
            
            for i, takeaway in enumerate(final_report.key_takeaways):
                st.markdown(f"""
                <div style="display: flex; align-items: flex-start; margin: 1rem 0; 
                            animation: slideInFromLeft 0.6s ease-out {i*0.1}s both;">
                    <div style="color: #10b981; font-size: 1.2rem; margin-right: 0.75rem; margin-top: 0.1rem;">
                        •
                    </div>
                    <div style="color: rgba(255,255,255,0.9); line-height: 1.5;">
                        {takeaway}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Recommendations with numbered styling
    if hasattr(final_report, "recommendations") and final_report.recommendations:
        with st.expander("💡 Strategic Recommendations", expanded=False):
            st.markdown("""
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; 
                        border-left: 4px solid #f093fb;">
            """, unsafe_allow_html=True)
            
            for i, rec in enumerate(final_report.recommendations, 1):
                st.markdown(f"""
                <div style="display: flex; align-items: flex-start; margin: 1rem 0; 
                            animation: slideInFromLeft 0.6s ease-out {i*0.1}s both;">
                    <div style="background: #f093fb; color: white; border-radius: 50%; 
                                width: 24px; height: 24px; display: flex; align-items: center; 
                                justify-content: center; font-size: 0.9rem; font-weight: 600; 
                                margin-right: 0.75rem; margin-top: 0.1rem; flex-shrink: 0;">
                        {i}
                    </div>
                    <div style="color: rgba(255,255,255,0.9); line-height: 1.5;">
                        {rec}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Sources with interactive links
    if hasattr(final_report, "sources") and final_report.sources:
        with st.expander("🔗 Research Sources", expanded=False):
            st.markdown("""
            <div style="background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; 
                        border-left: 4px solid #4facfe;">
            """, unsafe_allow_html=True)
            
            for i, source in enumerate(final_report.sources):
                # Try to make sources clickable if they're URLs
                if source.startswith(('http://', 'https://')):
                    display_text = source.replace('https://', '').replace('http://', '')[:60] + "..." if len(source) > 60 else source
                    st.markdown(f"""
                    <div style="margin: 0.75rem 0; animation: fadeIn 0.6s ease-out {i*0.1}s both;">
                        <a href="{source}" target="_blank" style="color: #4facfe; text-decoration: none; 
                           border-bottom: 1px solid rgba(79, 172, 254, 0.3); transition: all 0.3s ease;">
                            🔗 {display_text}
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="color: rgba(255,255,255,0.9); margin: 0.75rem 0; 
                                animation: fadeIn 0.6s ease-out {i*0.1}s both;">
                        • {source}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Enhanced download section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if hasattr(final_report, "to_markdown"):
            markdown_content = final_report.to_markdown()
            filename = f"ai_research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            st.download_button(
                label="📥 Download Complete Report",
                data=markdown_content,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
            )
            
            # File size info
            file_size_kb = len(markdown_content.encode('utf-8')) / 1024
            st.markdown(f"""
            <div style="text-align: center; margin-top: 0.5rem; color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                📊 Report size: {file_size_kb:.1f} KB • Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </div>
            """, unsafe_allow_html=True)


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

# =============================================================================
# Enhanced Main Application with Interactive UI
# =============================================================================

def main():
    """Main application entry point with enhanced UI and animations."""
    init_session_state()
    
    # Animated welcome header
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0; animation: fadeIn 1.2s ease-out;">
        <div class="header-title">🧠 AI Research Assistant Pro</div>
        <div class="header-subtitle">
            Multi-agent powered research with advanced AI orchestration
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced sidebar
    max_iterations, model_temp, max_search_results = render_enhanced_sidebar()
    
    # Main content area with glassmorphism
    st.markdown("""
    <div class="glass-container" style="animation: fadeIn 1s ease-out 0.3s both;">
    """, unsafe_allow_html=True)
    
    # Interactive input section
    st.markdown("""
    <h3 style="color: rgba(255,255,255,0.9); margin-bottom: 1rem; text-align: center;">
        🔍 What would you like to research today?
    </h3>
    """, unsafe_allow_html=True)
    
    # Enhanced input with examples
    example_queries = [
        "Latest developments in AI agents and their enterprise applications",
        "Current trends in quantum computing and commercial viability",
        "Impact of generative AI on software development practices",
        "Emerging blockchain technologies and real-world use cases"
    ]
    
    # Query input with improved styling
    query = st.text_area(
        "Research Topic",
        placeholder="Enter your research topic or question here...",
        height=120,
        label_visibility="collapsed",
        help="Be specific about what you want to research. The more detailed your query, the better the results."
    )
    
    # Example queries as clickable buttons
    st.markdown("""
    <p style="color: rgba(255,255,255,0.7); margin: 0.5rem 0; text-align: center;">
        💡 Try one of these example topics:
    </p>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, example in enumerate(example_queries):
        with cols[i % 2]:
            if st.button(f"📝 {example[:50]}{'...' if len(example) > 50 else ''}", 
                        key=f"example_{i}", 
                        help=example,
                        use_container_width=True):
                st.session_state["example_query"] = example
                st.rerun()
    
    # Use example query if selected
    if "example_query" in st.session_state:
        query = st.session_state["example_query"]
        del st.session_state["example_query"]
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Start button with enhanced styling
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_disabled = st.session_state.workflow_running or not query.strip()
        
        if start_disabled:
            button_text = "🔄 Processing..." if st.session_state.workflow_running else "🚀 Start Research"
        else:
            button_text = "🚀 Start AI Research"
        
        start_button = st.button(
            button_text,
            type="primary",
            disabled=start_disabled,
            use_container_width=True,
            help="Click to begin the multi-agent research process"
        )
    
    # Agent status display
    if st.session_state.workflow_running or any(status != "pending" 
                                               for status in st.session_state.agent_status.values()):
        render_interactive_agent_status()
    
    # Progress tracking containers
    if st.session_state.workflow_running:
        progress_container, status_container, metrics_container = create_animated_progress_display()
    else:
        progress_container = status_container = metrics_container = None
    
    # Execute workflow
    if start_button and query.strip():
        # Reset state with animations
        st.session_state.workflow_running = True
        st.session_state.workflow_result = None
        st.session_state.error = None
        st.session_state.agent_status = {
            "researcher": "pending",
            "analyst": "pending",
            "critic": "pending",
            "writer": "pending",
        }
        st.session_state.agent_completion_times = {}
        
        # Create progress containers
        progress_container, status_container, metrics_container = create_animated_progress_display()
        
        # Run enhanced workflow
        result = run_enhanced_workflow_with_progress(
            query.strip(),
            max_iterations,
            progress_container,
            status_container,
            metrics_container
        )
        
        st.session_state.workflow_result = result
        st.session_state.workflow_running = False
        
        # Refresh the page to show results with animation
        time.sleep(1)  # Allow final animations to complete
        st.rerun()
    
    # Display results with enhanced animations
    if st.session_state.workflow_result and not st.session_state.workflow_running:
        st.markdown("<br><br>", unsafe_allow_html=True)
        render_enhanced_report(st.session_state.workflow_result)
        render_enhanced_debug_info(st.session_state.workflow_result)
    
    # Error display with styling
    if st.session_state.error:
        st.markdown(f"""
        <div class="glass-container" style="border-left: 4px solid #ef4444; animation: bounce 0.8s ease-out;">
            <h4 style="color: #ef4444; margin-bottom: 1rem;">❌ Error Occurred</h4>
            <p style="color: rgba(255,255,255,0.8);">
                {st.session_state.error}
            </p>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.9rem;">
                Please check your configuration and try again.
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_enhanced_debug_info(result: dict):
    """Render enhanced debug information with interactive elements."""
    if not result:
        return
    
    with st.expander("🔧 Technical Details & Workflow Analytics", expanded=False):
        # Performance metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status = result.get("workflow_status", "Unknown")
            status_color = "#10b981" if status == "success" else "#ef4444" if status == "failed" else "#f59e0b"
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem; color: {status_color};">
                    {'✅' if status == 'success' else '❌' if status == 'failed' else '⚠️'}
                </div>
                <div style="font-size: 1rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                    {status.title()}
                </div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">Status</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            iterations = result.get("iteration_count", 0)
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem;">🔄</div>
                <div style="font-size: 1rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                    {iterations}
                </div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">Iterations</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            has_report = "Yes" if result.get("final_report") else "No"
            report_color = "#10b981" if has_report == "Yes" else "#ef4444"
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem; color: {report_color};">
                    {'📄' if has_report == 'Yes' else '📭'}
                </div>
                <div style="font-size: 1rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                    {has_report}
                </div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">Report Generated</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_time = st.session_state.workflow_start_time
            elapsed = time.time() - total_time if total_time else 0
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.2rem;">⏱️</div>
                <div style="font-size: 1rem; font-weight: 600; color: rgba(255,255,255,0.9);">
                    {elapsed:.1f}s
                </div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">Total Time</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Error details if present
        if result.get("error"):
            st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); 
                        border-radius: 12px; padding: 1rem; margin: 1rem 0;">
                <h5 style="color: #ef4444; margin-bottom: 0.5rem;">Error Details:</h5>
                <code style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">
                    {result['error']}
                </code>
            </div>
            """, unsafe_allow_html=True)
        
        # Critique result visualization
        if result.get("critique_result"):
            critique = result["critique_result"]
            st.markdown("<br>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if hasattr(critique, "quality_score"):
                    score_percent = int(critique.quality_score * 100)
                    score_color = "#10b981" if score_percent >= 70 else "#f59e0b" if score_percent >= 50 else "#ef4444"
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem;">
                        <h5 style="color: rgba(255,255,255,0.9); margin-bottom: 1rem;">Quality Score</h5>
                        <div style="display: flex; align-items: center;">
                            <div style="flex: 1; background: rgba(255,255,255,0.1); border-radius: 10px; height: 20px; margin-right: 1rem;">
                                <div style="width: {score_percent}%; background: {score_color}; height: 100%; border-radius: 10px; transition: width 1s ease;"></div>
                            </div>
                            <div style="color: {score_color}; font-weight: 600;">{score_percent}%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if hasattr(critique, "is_approved"):
                    approved = critique.is_approved
                    approval_color = "#10b981" if approved else "#ef4444"
                    approval_text = "Approved" if approved else "Needs Revision"
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem;">
                        <h5 style="color: rgba(255,255,255,0.9); margin-bottom: 1rem;">Approval Status</h5>
                        <div style="display: flex; align-items: center;">
                            <div style="color: {approval_color}; font-size: 1.5rem; margin-right: 0.5rem;">
                                {'✅' if approved else '❌'}
                            </div>
                            <div style="color: {approval_color}; font-weight: 600;">{approval_text}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
