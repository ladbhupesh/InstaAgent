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
    # Convert Pydantic model to dict if needed
    if state and hasattr(state, 'model_dump'):
        st.session_state.workflow_state = state.model_dump()
    else:
        st.session_state.workflow_state = state
    st.session_state.current_workflow_id = workflow_id
    return st.session_state.workflow_state


def get_workflow_state_dict(state):
    """Convert workflow state to dict if it's a Pydantic model."""
    if state is None:
        return None
    if isinstance(state, dict):
        return state
    if hasattr(state, 'model_dump'):
        return state.model_dump()
    # Fallback: try to access as attributes
    if hasattr(state, '__dict__'):
        return state.__dict__
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
                width='stretch'
            ):
                load_workflow_state(wf['workflow_id'])
                st.rerun()
    
    st.divider()
    
    # New workflow button
    if st.button("🆕 New Workflow", width='stretch'):
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
        submit = st.form_submit_button("Generate Concepts", width='stretch')
        
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

# Step 3 & 2: Check workflow state and route to appropriate screen
elif st.session_state.workflow_state:
    state = get_workflow_state_dict(st.session_state.workflow_state)
    
    if not state:
        st.info("No workflow state available.")
    else:
        # Check conditions
        is_completed = state.get("status") == "completed"
        has_video_path = state.get("video_path") and state.get("video_path").strip()
        has_images = state.get("image_paths") and len(state.get("image_paths", [])) > 0
        caption_data = state.get("caption") or {}
        has_caption = caption_data and (caption_data.get("full_caption") or caption_data.get("caption") or caption_data.get("hashtags"))
        has_results = has_video_path or has_images or has_caption
        has_concepts = state.get("concepts") and len(state.get("concepts", [])) > 0
        
        # Route 1: Show Results if completed or has results
        if is_completed or has_results:
            # Determine if this is a historic run
            video_path = state.get("video_path")
            video_exists = video_path and Path(video_path).exists()
            
            if video_exists:
                st.header("✅ Video Created Successfully!")
            else:
                st.header("📁 Historic Workflow")
                if video_path:
                    st.warning(f"⚠️ Video file not found at: {video_path}")
                else:
                    st.info("This workflow was completed but the video file is no longer available.")
            
            st.info(f"Workflow ID: `{st.session_state.current_workflow_id}`")
            
            # Display video if it exists
            if video_exists:
                st.subheader("Final Video")
                st.video(video_path)
                
                # Download button
                with open(video_path, "rb") as video_file:
                    st.download_button(
                        label="📥 Download Video",
                        data=video_file,
                        file_name="instagram_reel.mp4",
                        mime="video/mp4",
                        width='stretch'
                    )
            
            # Display generated images (for both new and historic runs)
            image_paths = state.get("image_paths", [])
            if image_paths:
                st.subheader("🖼️ Generated Images")
                st.markdown("Images used in the final video:")
                
                # Filter out non-existent paths
                valid_images = [Path(img) for img in image_paths if Path(img).exists()]
                
                if valid_images:
                    # Display images in a grid
                    num_cols = 3
                    num_images = len(valid_images)
                    
                    for i in range(0, num_images, num_cols):
                        cols = st.columns(num_cols)
                        for j, col in enumerate(cols):
                            if i + j < num_images:
                                img_path = valid_images[i + j]
                                with col:
                                    st.image(str(img_path))
                                    st.caption(f"Image {i + j + 1}: {img_path.name}")
                else:
                    st.info("ℹ️ Image files not found. They may have been moved or deleted.")
            
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
            
            # Display caption - Make it prominent (for both new and historic runs)
            if state.get("caption"):
                caption_data = state["caption"]
                st.subheader("📝 Instagram Caption & Hashtags")
                st.markdown("**Ready to copy and paste into your Instagram post:**")
                
                # Display full caption in a text area for easy copying
                full_caption = caption_data.get("full_caption", "")
                if full_caption:
                    st.text_area(
                        "📋 Copy this caption:",
                        value=full_caption,
                        height=250,
                        key=f"caption_display_{st.session_state.current_workflow_id}",
                        help="Select all and copy (Ctrl+A, Ctrl+C) to use in your Instagram post",
                        label_visibility="visible"
                    )
                    
                    # Download caption as text file
                    st.download_button(
                        label="📥 Download Caption as Text File",
                        data=full_caption,
                        file_name=f"instagram_caption_{st.session_state.current_workflow_id}.txt",
                        mime="text/plain",
                        width='stretch'
                    )
                
                # Display caption breakdown in an expander
                with st.expander("📊 View Caption Details"):
                    st.markdown(f"**Main Caption Text:**\n\n{caption_data.get('caption', 'N/A')}")
                    
                    hashtags = caption_data.get("hashtags", [])
                    if hashtags:
                        st.markdown(f"**Hashtags ({len(hashtags)} total):**")
                        hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                        st.code(hashtag_text, language=None)
                        st.markdown(f"*Copy the hashtags above to add to your post*")
            
            # Display concept details
            if state.get("concepts") and state.get("selected_concept_index") is not None:
                selected_concept = state["concepts"][state["selected_concept_index"]]
                with st.expander("💡 Selected Concept Details"):
                    st.json(selected_concept)
            
            # Create new workflow button
            if st.button("🆕 Create New Workflow", width='stretch'):
                st.session_state.current_workflow_id = None
                st.session_state.workflow_state = None
                st.rerun()
        
        # Route 2: Show Concept Selection if has concepts but not completed and no results
        elif has_concepts and not is_completed and not has_results:
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
                    
                    if st.button(f"Select Concept {i+1}", key=f"select_{i}", width='stretch'):
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
        
        # Route 3: Show error state if failed
        elif state.get("status") == "failed":
            st.error("❌ Workflow Failed")
            st.error(f"Error: {state.get('error_message', 'Unknown error')}")
            
            if st.button("🔄 Retry", width='stretch'):
                # Reset to concept selection
                if state.get("concepts"):
                    st.session_state.workflow_state = {
                        **state,
                        "status": "waiting_for_selection",
                        "current_step": "concept_selection"
                    }
                    st.rerun()
        
        # Route 4: Show loading/in-progress state
        else:
            current_step = state.get("current_step", "unknown")
            
            st.info(f"⏳ Current Step: {current_step.replace('_', ' ').title()}")
            st.progress(0.5)  # Placeholder progress
            
            if st.button("🔄 Refresh Status", width='stretch'):
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
