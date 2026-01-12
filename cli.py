"""CLI interface for Instagram Reels creation workflow."""

import asyncio
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from orchestrator.workflow import ReelsWorkflow
from orchestrator.state_manager import StateManager


class CLI:
    """Command-line interface for the Reels workflow."""
    
    def __init__(self):
        self.workflow = ReelsWorkflow()
        self.state_manager = StateManager()
    
    def print_header(self):
        """Print CLI header."""
        print("\n" + "="*60)
        print("🎬 Instagram Reels AI Creator - CLI")
        print("="*60 + "\n")
    
    def print_concepts(self, concepts: list):
        """Print concepts in a formatted way."""
        print("\n" + "-"*60)
        print("Generated Concepts:")
        print("-"*60 + "\n")
        
        for i, concept in enumerate(concepts, 1):
            print(f"Concept {i}: {concept.get('title', 'Untitled')}")
            print(f"  Hook: {concept.get('hook', 'N/A')}")
            print(f"  Value: {concept.get('value_proposition', 'N/A')}")
            print(f"  Style: {concept.get('visual_style', 'N/A')}")
            print()
    
    def select_concept(self, concepts: list) -> int:
        """Prompt user to select a concept."""
        while True:
            try:
                choice = input("Select a concept (1-3): ").strip()
                index = int(choice) - 1
                
                if 0 <= index < len(concepts):
                    return index
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    async def create_reel(self):
        """Main workflow for creating a reel."""
        self.print_header()
        
        # Step 1: Get input
        print("Step 1: Provide your niche and keywords\n")
        niche = input("Enter niche/topic: ").strip()
        if not niche:
            print("Error: Niche is required.")
            return
        
        keywords = input("Enter keywords (optional, press Enter to skip): ").strip()
        
        # Step 2: Generate concepts
        print("\n⏳ Generating concepts... This may take a minute.\n")
        try:
            result = await self.workflow.start_workflow(
                niche=niche,
                keywords=keywords
            )
            
            workflow_id = result["workflow_id"]
            concepts = result.get("concepts", [])
            
            # Check for errors first
            if result.get("status") == "failed":
                error_msg = result.get("error_message", "Unknown error")
                print(f"❌ Error generating concepts: {error_msg}")
                return
            
            if not concepts:
                # Check if there's an error message
                error_msg = result.get("error_message", "No concepts were generated")
                print(f"❌ Error: {error_msg}")
                print(f"Status: {result.get('status', 'unknown')}")
                return
            
            self.print_concepts(concepts)
            
            # Step 3: Select concept
            selected_index = self.select_concept(concepts)
            print(f"\n✓ Selected: Concept {selected_index + 1}\n")
            
            # Step 4: Generate script, images, and video
            print("⏳ Generating script, images, and video...")
            print("This will take several minutes. Please wait...\n")
            
            result = await self.workflow.continue_workflow(
                workflow_id=workflow_id,
                selected_concept_index=selected_index
            )
            
            # Step 5: Display results
            if result.get("status") == "completed":
                video_path = result.get("video_path")
                print("\n" + "="*60)
                print("✅ Video Created Successfully!")
                print("="*60 + "\n")
                
                if video_path:
                    print(f"Video saved at: {video_path}\n")
                    
                    # Display script summary
                    script = result.get("script", {})
                    if script:
                        print("Script Summary:")
                        print(f"  Total Duration: {script.get('total_duration', 0):.1f} seconds")
                        print(f"  Segments: {len(script.get('segments', []))}")
                        print()
                    
                    # Display caption
                    caption = result.get("caption")
                    if caption:
                        print("-"*60)
                        print("📝 Instagram Caption:")
                        print("-"*60)
                        print()
                        print(caption.get("full_caption", ""))
                        print()
                        print(f"Hashtags ({len(caption.get('hashtags', []))}):")
                        hashtags = caption.get("hashtags", [])
                        if hashtags:
                            hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
                            print(f"  {hashtag_str}")
                        print()
                
                print("🎉 Your Instagram Reel is ready!")
            else:
                print(f"\n❌ Error: {result.get('error_message', 'Unknown error')}")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def list_workflows(self):
        """List all saved workflows."""
        workflows = self.state_manager.list_workflows()
        
        if not workflows:
            print("No saved workflows found.")
            return
        
        print("\n" + "="*60)
        print("Saved Workflows:")
        print("="*60 + "\n")
        
        for wf in workflows:
            print(f"ID: {wf['workflow_id']}")
            print(f"  Niche: {wf.get('niche', 'N/A')}")
            print(f"  Status: {wf.get('status', 'N/A')}")
            print(f"  Step: {wf.get('current_step', 'N/A')}")
            print(f"  Updated: {wf.get('updated_at', 'N/A')}")
            print()
    
    def resume_workflow(self, workflow_id: str):
        """Resume an existing workflow."""
        state = self.state_manager.load_state(workflow_id)
        
        if not state:
            print(f"Workflow {workflow_id} not found.")
            return
        
        print(f"\nResuming workflow: {workflow_id}")
        print(f"Current step: {state.current_step}")
        print(f"Status: {state.status}\n")
        
        if state.concepts and state.selected_concept_index is None:
            # Need to select concept
            self.print_concepts(state.concepts)
            selected_index = self.select_concept(state.concepts)
            
            print(f"\n⏳ Continuing workflow...\n")
            asyncio.run(
                self.workflow.continue_workflow(workflow_id, selected_index)
            )
        elif state.status == "completed":
            print("✅ This workflow is already completed.")
            if state.video_path:
                print(f"Video: {state.video_path}")
        else:
            print(f"Current status: {state.status}")
            if state.error_message:
                print(f"Error: {state.error_message}")


def main():
    """Main CLI entry point."""
    cli = CLI()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            cli.list_workflows()
        elif command == "resume" and len(sys.argv) > 2:
            cli.resume_workflow(sys.argv[2])
        else:
            print("Usage:")
            print("  python cli.py              - Create new reel")
            print("  python cli.py list         - List saved workflows")
            print("  python cli.py resume <id>  - Resume a workflow")
    else:
        asyncio.run(cli.create_reel())


if __name__ == "__main__":
    main()
