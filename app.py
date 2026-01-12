"""Streamlit UI for Instagram Reels creation workflow."""

import streamlit as st
import asyncio
from pathlib import Path
import json
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from orchestrator.workflow import ReelsWorkflow
from orchestrator.state_manager import StateManager


# Page configuration
st.set_page_config(
    page_title="Instagram Reels AI Creator",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if "workflow" not in st.session_state:
    st.session_state.workflow = None
if "current_workflow_id" not in st.session_state:
    st.session_state.current_workflow_id = None
if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None


def init_workflow():
    """Initialize workflow instance."""
    if st.session_state.workflow is None:
        try:
            st.session_state.workflow = ReelsWorkflow()
        except Exception as e:
            st.error(f"Failed to initialize workflow: {e}")
            st.stop()


def load_workflow_state(workflow_id: str):
    """Load and display workflow state."""
    init_workflow()
    state = st.session_state.workflow.load_workflow_state(workflow_id)
    st.session_state.workflow_state = state
    st.session_state.current_workflow_id = workflow_id
    return state


# Main UI
st.title("🎬 Instagram Reels AI Creator")
st.markdown("Create engaging Instagram Reels using AI-powered multi-agent workflow")

# Sidebar for workflow management
with st.sidebar:
    st.header("Workflow Management")
    
    # List existing workflows
    state_manager = StateManager()
    workflows = state_manager.list_workflows()
    
    if workflows:
        st.subheader("Existing Workflows")
        for wf in workflows[:10]:  # Show last 10
            if st.button(
                f"📁 {wf['workflow_id'][:8]}... - {wf.get('niche', 'N/A')}",
                key=f"load_{wf['workflow_id']}",
                use_container_width=True
            ):
                load_workflow_state(wf['workflow_id'])
                st.rerun()
    
    st.divider()
    
    # New workflow button
    if st.button("🆕 New Workflow", use_container_width=True):
        st.session_state.current_workflow_id = None
        st.session_state.workflow_state = None
        st.rerun()


# Main content area
init_workflow()

# Step 1: Input and Concept Generation
if st.session_state.current_workflow_id is None:
    st.header("Step 1: Generate Concepts")
    
    with st.form("concept_generation_form"):
        niche = st.text_input(
            "Niche/Topic *",
            placeholder="e.g., fitness, cooking, tech tips, productivity"
        )
        keywords = st.text_input(
            "Keywords (optional)",
            placeholder="e.g., beginner-friendly, quick tips, trending"
        )
        submit = st.form_submit_button("Generate Concepts", use_container_width=True)
        
        if submit:
            if not niche:
                st.error("Please enter a niche/topic")
            else:
                with st.spinner("Generating concepts... This may take a minute."):
                    try:
                        result = asyncio.run(
                            st.session_state.workflow.start_workflow(
                                niche=niche,
                                keywords=keywords
                            )
                        )
                        
                        st.session_state.current_workflow_id = result["workflow_id"]
                        st.session_state.workflow_state = result
                        st.success("Concepts generated! Please select one below.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating concepts: {e}")

# Step 2: Concept Selection
elif st.session_state.workflow_state and st.session_state.workflow_state.get("concepts"):
    state = st.session_state.workflow_state
    
    st.header("Step 2: Select a Concept")
    st.info(f"Workflow ID: `{st.session_state.current_workflow_id}`")
    
    concepts = state.get("concepts", [])
    
    # Display concepts in columns
    cols = st.columns(3)
    
    selected_index = None
    for i, concept in enumerate(concepts):
        with cols[i]:
            st.subheader(f"Concept {i+1}: {concept.get('title', 'Untitled')}")
            st.markdown(f"**Hook:** {concept.get('hook', 'N/A')}")
            st.markdown(f"**Value:** {concept.get('value_proposition', 'N/A')}")
            st.markdown(f"**Style:** {concept.get('visual_style', 'N/A')}")
            st.markdown(f"**Audience:** {concept.get('target_audience', 'N/A')}")
            
            if st.button(f"Select Concept {i+1}", key=f"select_{i}", use_container_width=True):
                selected_index = i
    
    if selected_index is not None:
        with st.spinner("Generating script, images, and video... This will take several minutes."):
            try:
                result = asyncio.run(
                    st.session_state.workflow.continue_workflow(
                        workflow_id=st.session_state.current_workflow_id,
                        selected_concept_index=selected_index
                    )
                )
                
                st.session_state.workflow_state = result
                st.success("Video creation complete!")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating video: {e}")

# Step 3: Display Results
elif st.session_state.workflow_state and st.session_state.workflow_state.get("video_path"):
    state = st.session_state.workflow_state
    
    st.header("✅ Video Created Successfully!")
    st.info(f"Workflow ID: `{st.session_state.current_workflow_id}`")
    
    # Display video
    video_path = state.get("video_path")
    if video_path and Path(video_path).exists():
        st.subheader("Final Video")
        st.video(video_path)
        
        # Download button
        with open(video_path, "rb") as video_file:
            st.download_button(
                label="📥 Download Video",
                data=video_file,
                file_name="instagram_reel.mp4",
                mime="video/mp4",
                use_container_width=True
            )
    
    # Display script
    if state.get("script"):
        script = state["script"]
        with st.expander("📝 View Script"):
            st.markdown(f"**Full Transcript:**\n\n{script.get('full_transcript', 'N/A')}")
            st.markdown(f"**Hook Enhancement:**\n\n{script.get('hook_enhancement', 'N/A')}")
            st.markdown(f"**Pacing Notes:**\n\n{script.get('pacing_notes', 'N/A')}")
            
            st.subheader("Script Segments")
            for i, segment in enumerate(script.get("segments", []), 1):
                st.markdown(f"**Segment {i}** ({segment.get('duration_estimate', 0):.1f}s)")
                st.markdown(f"*Spoken:* {segment.get('spoken_text', 'N/A')}")
                st.markdown(f"*Visual:* {segment.get('visual_description', 'N/A')}")
                st.divider()
    
    # Display concept details
    if state.get("concepts") and state.get("selected_concept_index") is not None:
        selected_concept = state["concepts"][state["selected_concept_index"]]
        with st.expander("💡 Selected Concept Details"):
            st.json(selected_concept)
    
    # Create new workflow button
    if st.button("🆕 Create New Workflow", use_container_width=True):
        st.session_state.current_workflow_id = None
        st.session_state.workflow_state = None
        st.rerun()

# Error state
elif st.session_state.workflow_state and st.session_state.workflow_state.get("status") == "failed":
    state = st.session_state.workflow_state
    
    st.error("❌ Workflow Failed")
    st.error(f"Error: {state.get('error_message', 'Unknown error')}")
    
    if st.button("🔄 Retry", use_container_width=True):
        # Reset to concept selection
        if state.get("concepts"):
            st.session_state.workflow_state = {
                **state,
                "status": "waiting_for_selection",
                "current_step": "concept_selection"
            }
            st.rerun()

# Loading/In Progress state
elif st.session_state.workflow_state:
    state = st.session_state.workflow_state
    current_step = state.get("current_step", "unknown")
    
    st.info(f"⏳ Current Step: {current_step.replace('_', ' ').title()}")
    st.progress(0.5)  # Placeholder progress
    
    if st.button("🔄 Refresh Status", use_container_width=True):
        # Reload state
        if st.session_state.current_workflow_id:
            load_workflow_state(st.session_state.current_workflow_id)
            st.rerun()

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Instagram Reels AI Creator | Powered by LangGraph, OpenAI, ElevenLabs</p>
    </div>
    """,
    unsafe_allow_html=True
)
