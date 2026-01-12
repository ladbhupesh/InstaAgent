"""Agent D: Voice & Video Assembler - Creates voiceover and assembles final video."""

import asyncio
from pathlib import Path
from typing import List, Optional

from utils.api_clients import ElevenLabsClient
from utils.video_utils import VideoProcessor


class VideoAssembler:
    """Agent D: Generates voiceover and assembles final video."""
    
    def __init__(self):
        self.tts_client = ElevenLabsClient()
        self.video_processor = VideoProcessor()
    
    async def generate_voiceover(
        self,
        transcript: str,
        output_path: Path,
        voice_id: Optional[str] = None
    ) -> Path:
        """
        Generate voiceover audio from transcript.
        
        Args:
            transcript: The full spoken transcript
            output_path: Path where audio file will be saved
            voice_id: Optional custom voice ID (uses default if not provided)
        
        Returns:
            Path to the generated audio file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate speech
        await self.tts_client.generate_speech(
            text=transcript,
            output_path=output_path,
            voice_id=voice_id
        )
        
        if not output_path.exists():
            raise Exception(f"Voiceover file was not created: {output_path}")
        
        print(f"Generated voiceover: {output_path.name}")
        return output_path
    
    async def assemble_video(
        self,
        image_paths: List[Path],
        audio_path: Path,
        output_path: Path,
        image_durations: Optional[List[float]] = None
    ) -> Path:
        """
        Assemble final video from images and audio.
        
        Args:
            image_paths: List of paths to image files (in order)
            audio_path: Path to voiceover audio file
            output_path: Path where final video will be saved
            image_durations: Optional list of durations for each image.
                           If None, images are evenly distributed across audio duration.
        
        Returns:
            Path to the created video file
        """
        # Validate inputs
        if not image_paths:
            raise ValueError(
                "Cannot assemble video: No images provided. "
                "Please ensure image generation completed successfully."
            )
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Verify all image files exist
        missing_images = [str(p) for p in image_paths if not p.exists()]
        if missing_images:
            raise FileNotFoundError(
                f"Some image files are missing: {', '.join(missing_images)}"
            )
        
        # This is a CPU-intensive operation, run in executor
        loop = asyncio.get_event_loop()
        
        video_path = await loop.run_in_executor(
            None,
            lambda: self.video_processor.create_reel(
                image_paths=image_paths,
                audio_path=audio_path,
                output_path=output_path,
                image_durations=image_durations
            )
        )
        
        if not video_path.exists():
            raise Exception(f"Video file was not created: {video_path}")
        
        print(f"Created video: {video_path.name}")
        return video_path
    
    async def create_complete_reel(
        self,
        transcript: str,
        image_paths: List[Path],
        output_dir: Path,
        video_filename: str = "final_reel.mp4",
        voice_id: Optional[str] = None,
        image_durations: Optional[List[float]] = None
    ) -> Path:
        """
        Complete workflow: generate voiceover and assemble video.
        
        Args:
            transcript: The full spoken transcript
            image_paths: List of paths to image files
            output_dir: Directory for output files
            video_filename: Name for the final video file
            voice_id: Optional custom voice ID
            image_durations: Optional durations for each image
        
        Returns:
            Path to the final video file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate voiceover
        audio_path = output_dir / "voiceover.mp3"
        await self.generate_voiceover(
            transcript=transcript,
            output_path=audio_path,
            voice_id=voice_id
        )
        
        # Assemble video
        video_path = output_dir / video_filename
        await self.assemble_video(
            image_paths=image_paths,
            audio_path=audio_path,
            output_path=video_path,
            image_durations=image_durations
        )
        
        return video_path
