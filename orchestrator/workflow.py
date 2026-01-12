"""LangGraph workflow orchestrator for Instagram Reels creation."""

import asyncio
from pathlib import Path
from typing import Dict, Any, TypedDict, Annotated, Optional
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from agents.concept_strategist import ConceptStrategist, ReelConcept
from agents.scriptwriter import Scriptwriter, ReelScript
from agents.media_generator import MediaGenerator
from agents.video_assembler import VideoAssembler
from orchestrator.state_manager import StateManager, WorkflowState


class WorkflowStateDict(TypedDict):
    """State dictionary for LangGraph workflow."""
    workflow_id: str
    niche: str
    keywords: str
    concepts: list
    selected_concept_index: int
    script: dict
    image_paths: list
    audio_path: str
    video_path: str
    current_step: str
    status: str
    error_message: str
    output_dir: str


class ReelsWorkflow:
    """Master orchestrator for Instagram Reels creation workflow."""
    
    def __init__(self, state_storage_path: Path = Path("./state")):
        self.state_manager = StateManager(state_storage_path)
        self.concept_strategist = ConceptStrategist()
        self.scriptwriter = Scriptwriter()
        self.media_generator = MediaGenerator()
        self.video_assembler = VideoAssembler()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(WorkflowStateDict)
        
        # Add nodes
        workflow.add_node("generate_concepts", self._generate_concepts_node)
        workflow.add_node("generate_script", self._generate_script_node)
        workflow.add_node("generate_images", self._generate_images_node)
        workflow.add_node("assemble_video", self._assemble_video_node)
        workflow.add_node("save_state", self._save_state_node)
        
        # Define edges
        workflow.set_entry_point("generate_concepts")
        workflow.add_edge("generate_concepts", "save_state")
        
        # Conditional edge: after concepts are generated, wait for user selection
        # (In practice, this will be handled by the UI/CLI)
        workflow.add_edge("save_state", END)
        
        return workflow.compile()
    
    async def _generate_concepts_node(self, state: WorkflowStateDict) -> WorkflowStateDict:
        """Node: Generate concepts."""
        try:
            concepts = await self.concept_strategist.generate_concepts(
                niche=state["niche"],
                keywords=state.get("keywords", ""),
                additional_context=""
            )
            
            # Convert Pydantic models to dicts
            concepts_dict = [concept.model_dump() for concept in concepts]
            
            state["concepts"] = concepts_dict
            state["current_step"] = "concept_selection"
            state["status"] = "waiting_for_selection"
            
        except Exception as e:
            state["status"] = "failed"
            state["error_message"] = f"Concept generation failed: {str(e)}"
        
        return state
    
    async def _generate_script_node(self, state: WorkflowStateDict) -> WorkflowStateDict:
        """Node: Generate script."""
        try:
            selected_concept = state["concepts"][state["selected_concept_index"]]
            
            script = await self.scriptwriter.generate_script(
                concept=selected_concept,
                target_duration=30.0
            )
            
            state["script"] = script.model_dump()
            state["current_step"] = "script_generation"
            state["status"] = "in_progress"
            
        except Exception as e:
            state["status"] = "failed"
            state["error_message"] = f"Script generation failed: {str(e)}"
        
        return state
    
    async def _generate_images_node(self, state: WorkflowStateDict) -> WorkflowStateDict:
        """Node: Generate images."""
        try:
            script_data = state["script"]
            segments = script_data.get("segments", [])
            
            image_prompts = [seg["image_prompt"] for seg in segments]
            
            output_dir = Path(state.get("output_dir", "./output")) / state["workflow_id"]
            output_dir.mkdir(parents=True, exist_ok=True)
            
            image_paths = await self.media_generator.generate_images(
                image_prompts=image_prompts,
                output_dir=output_dir / "images",
                prefix="reel_image"
            )
            
            state["image_paths"] = [str(p) for p in image_paths]
            state["current_step"] = "image_generation"
            state["status"] = "in_progress"
            
        except Exception as e:
            state["status"] = "failed"
            state["error_message"] = f"Image generation failed: {str(e)}"
        
        return state
    
    async def _assemble_video_node(self, state: WorkflowStateDict) -> WorkflowStateDict:
        """Node: Assemble final video."""
        try:
            script_data = state["script"]
            transcript = script_data.get("full_transcript", "")
            segments = script_data.get("segments", [])
            
            image_paths = [Path(p) for p in state["image_paths"]]
            image_durations = [seg.get("duration_estimate", 0) for seg in segments]
            
            output_dir = Path(state.get("output_dir", "./output")) / state["workflow_id"]
            
            video_path = await self.video_assembler.create_complete_reel(
                transcript=transcript,
                image_paths=image_paths,
                output_dir=output_dir,
                video_filename="final_reel.mp4",
                image_durations=image_durations
            )
            
            state["video_path"] = str(video_path)
            state["audio_path"] = str(output_dir / "voiceover.mp3")
            state["current_step"] = "video_assembly"
            state["status"] = "completed"
            
        except Exception as e:
            state["status"] = "failed"
            state["error_message"] = f"Video assembly failed: {str(e)}"
        
        return state
    
    async def _save_state_node(self, state: WorkflowStateDict) -> WorkflowStateDict:
        """Node: Save state to disk."""
        try:
            workflow_state = WorkflowState(
                workflow_id=state["workflow_id"],
                niche=state.get("niche"),
                keywords=state.get("keywords"),
                concepts=state.get("concepts"),
                selected_concept_index=state.get("selected_concept_index"),
                script=state.get("script"),
                image_paths=state.get("image_paths"),
                audio_path=state.get("audio_path"),
                video_path=state.get("video_path"),
                current_step=state.get("current_step", "concept_generation"),
                status=state.get("status", "in_progress"),
                error_message=state.get("error_message")
            )
            
            self.state_manager.save_state(workflow_state)
            
        except Exception as e:
            print(f"Error saving state: {e}")
        
        return state
    
    async def start_workflow(
        self,
        niche: str,
        keywords: str = "",
        workflow_id: Optional[str] = None,
        output_dir: str = "./output"
    ) -> Dict[str, Any]:
        """
        Start a new workflow.
        
        Returns:
            Initial state with generated concepts
        """
        if not workflow_id:
            workflow_id = str(uuid.uuid4())
        
        initial_state: WorkflowStateDict = {
            "workflow_id": workflow_id,
            "niche": niche,
            "keywords": keywords,
            "concepts": [],
            "selected_concept_index": -1,
            "script": {},
            "image_paths": [],
            "audio_path": "",
            "video_path": "",
            "current_step": "concept_generation",
            "status": "in_progress",
            "error_message": "",
            "output_dir": output_dir
        }
        
        # Run workflow up to concept generation
        result = await self.workflow.ainvoke(initial_state)
        
        return result
    
    async def continue_workflow(
        self,
        workflow_id: str,
        selected_concept_index: int
    ) -> Dict[str, Any]:
        """
        Continue workflow after concept selection.
        
        Args:
            workflow_id: The workflow ID
            selected_concept_index: Index of selected concept (0-2)
        
        Returns:
            Updated state
        """
        # Load existing state
        saved_state = self.state_manager.load_state(workflow_id)
        if not saved_state:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Convert to workflow state dict
        state: WorkflowStateDict = {
            "workflow_id": saved_state.workflow_id,
            "niche": saved_state.niche or "",
            "keywords": saved_state.keywords or "",
            "concepts": saved_state.concepts or [],
            "selected_concept_index": selected_concept_index,
            "script": saved_state.script or {},
            "image_paths": saved_state.image_paths or [],
            "audio_path": saved_state.audio_path or "",
            "video_path": saved_state.video_path or "",
            "current_step": saved_state.current_step,
            "status": saved_state.status,
            "error_message": saved_state.error_message or "",
            "output_dir": "./output"
        }
        
        # Continue workflow: generate script, images, and video
        # We'll manually execute the remaining nodes
        state = await self._generate_script_node(state)
        state = await self._save_state_node(state)
        
        if state["status"] != "failed":
            state = await self._generate_images_node(state)
            state = await self._save_state_node(state)
        
        if state["status"] != "failed":
            state = await self._assemble_video_node(state)
            state = await self._save_state_node(state)
        
        return state
    
    def load_workflow_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow state."""
        return self.state_manager.load_state(workflow_id)
