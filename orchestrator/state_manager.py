"""State management for workflow persistence."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    """Complete workflow state that can be saved and restored."""
    workflow_id: str = Field(description="Unique identifier for this workflow")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Step 1: Concept Generation
    niche: Optional[str] = None
    keywords: Optional[str] = None
    concepts: Optional[list] = None
    selected_concept_index: Optional[int] = None
    
    # Step 2: Script Generation
    script: Optional[Dict[str, Any]] = None
    
    # Step 3: Media Generation
    image_paths: Optional[list] = None
    
    # Step 4: Video Assembly
    audio_path: Optional[str] = None
    video_path: Optional[str] = None
    
    # Metadata
    current_step: str = "concept_generation"
    status: str = "in_progress"  # in_progress, completed, failed
    error_message: Optional[str] = None


class StateManager:
    """Manages workflow state persistence."""
    
    def __init__(self, storage_path: Path = Path("./state")):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def save_state(self, state: WorkflowState) -> Path:
        """Save workflow state to disk."""
        state.updated_at = datetime.now().isoformat()
        
        state_file = self.storage_path / f"{state.workflow_id}.json"
        
        with open(state_file, "w") as f:
            json.dump(state.model_dump(), f, indent=2)
        
        return state_file
    
    def load_state(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow state from disk."""
        state_file = self.storage_path / f"{workflow_id}.json"
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
            
            return WorkflowState(**data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading state: {e}")
            return None
    
    def list_workflows(self) -> list[Dict[str, Any]]:
        """List all saved workflows."""
        workflows = []
        
        for state_file in self.storage_path.glob("*.json"):
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                
                workflows.append({
                    "workflow_id": data.get("workflow_id"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "current_step": data.get("current_step"),
                    "status": data.get("status"),
                    "niche": data.get("niche")
                })
            except Exception as e:
                print(f"Error reading {state_file}: {e}")
        
        return sorted(workflows, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    def delete_state(self, workflow_id: str) -> bool:
        """Delete a workflow state."""
        state_file = self.storage_path / f"{workflow_id}.json"
        
        if state_file.exists():
            state_file.unlink()
            return True
        
        return False
