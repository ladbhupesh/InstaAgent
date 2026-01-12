"""Video processing utilities using MoviePy."""

import os
from pathlib import Path
from typing import List, Optional

# MoviePy imports - supports both v1.x and v2.x
try:
    # Try v2.x first (direct imports)
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
    from moviepy import concatenate_videoclips
    try:
        from moviepy.config import check_ffmpeg
        HAS_CHECK_FFMPEG = True
    except ImportError:
        # MoviePy v2 doesn't have check_ffmpeg, use alternative
        from moviepy.config import get_exe
        HAS_CHECK_FFMPEG = False
    MOVIEPY_V2 = True
except ImportError:
    # Fallback to v1.x (editor module)
    try:
        from moviepy.editor import (
            ImageClip, AudioFileClip, CompositeVideoClip,
            concatenate_videoclips
        )
        try:
            from moviepy.config import check_ffmpeg
            HAS_CHECK_FFMPEG = True
        except ImportError:
            from moviepy.config import get_exe
            HAS_CHECK_FFMPEG = False
        MOVIEPY_V2 = False
    except ImportError as e:
        raise ImportError(
            "MoviePy is not installed. Install it with: pip install moviepy"
        ) from e


def _check_ffmpeg_available():
    """Check if FFmpeg is available - works with both MoviePy v1 and v2."""
    if HAS_CHECK_FFMPEG:
        # MoviePy v1.x has check_ffmpeg function
        return check_ffmpeg()
    else:
        # MoviePy v2.x - use FFMPEG_BINARY or get_exe() to check
        try:
            from moviepy.config import FFMPEG_BINARY, get_exe
            import os
            
            # Try to get FFmpeg path from config
            try:
                ffmpeg_path = FFMPEG_BINARY
            except (AttributeError, NameError):
                ffmpeg_path = get_exe()
            
            # Check if path exists and is not empty
            if ffmpeg_path and ffmpeg_path != '':
                return os.path.exists(ffmpeg_path) or os.access(ffmpeg_path, os.X_OK)
            
            # Fallback: try to run ffmpeg command directly
            import subprocess
            try:
                result = subprocess.run(
                    ['ffmpeg', '-version'],
                    capture_output=True,
                    timeout=5,
                    check=False
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                return False
        except Exception:
            # Final fallback: try to run ffmpeg command
            import subprocess
            try:
                result = subprocess.run(
                    ['ffmpeg', '-version'],
                    capture_output=True,
                    timeout=5,
                    check=False
                )
                return result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                return False


class VideoProcessor:
    """Video processing utilities for creating Instagram Reels."""
    
    def __init__(self):
        # Check if FFmpeg is available
        if not _check_ffmpeg_available():
            raise RuntimeError(
                "FFmpeg is not installed. Please install it:\n"
                "macOS: brew install ffmpeg\n"
                "Ubuntu: sudo apt-get install ffmpeg\n"
                "Windows: Download from https://ffmpeg.org/download.html"
            )
        
        self.resolution = os.getenv("VIDEO_RESOLUTION", "1080x1920").split("x")
        self.width = int(self.resolution[0])
        self.height = int(self.resolution[1])
        self.fps = int(os.getenv("VIDEO_FPS", "30"))
        self.audio_bitrate = os.getenv("AUDIO_BITRATE", "192k")
    
    def create_reel(
        self,
        image_paths: List[Path],
        audio_path: Path,
        output_path: Path,
        image_durations: Optional[List[float]] = None
    ) -> Path:
        """
        Create an Instagram Reel from images and audio.
        
        Args:
            image_paths: List of paths to image files
            audio_path: Path to audio file (voiceover)
            output_path: Path where the final video will be saved
            image_durations: Optional list of durations for each image.
                            If None, images are evenly distributed across audio duration.
        
        Returns:
            Path to the created video file
        """
        # Validate inputs
        if not image_paths:
            raise ValueError("Cannot create video: image_paths list is empty")
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load audio to get total duration
        audio_clip = AudioFileClip(str(audio_path))
        total_duration = audio_clip.duration
        
        # Calculate image durations if not provided
        if image_durations is None:
            duration_per_image = total_duration / len(image_paths)
            image_durations = [duration_per_image] * len(image_paths)
        
        # Ensure durations sum to audio duration
        total_image_duration = sum(image_durations)
        if total_image_duration != total_duration:
            # Scale durations proportionally
            scale_factor = total_duration / total_image_duration
            image_durations = [d * scale_factor for d in image_durations]
        
        # Create video clips from images
        video_clips = []
        current_time = 0
        
        for image_path, duration in zip(image_paths, image_durations):
            if MOVIEPY_V2:
                # MoviePy v2 API - uses method chaining with 'with_' prefix
                clip = ImageClip(str(image_path)).with_duration(duration)
                clip = clip.resized((self.width, self.height))
                clip = clip.with_start(current_time)
            else:
                # MoviePy v1 API - uses positional args and 'set_' methods
                clip = ImageClip(str(image_path), duration=duration)
                clip = clip.resize((self.width, self.height))
                clip = clip.set_start(current_time)
            video_clips.append(clip)
            current_time += duration
        
        # Concatenate all clips
        final_video = concatenate_videoclips(video_clips, method="compose")
        
        # Add audio
        if MOVIEPY_V2:
            # MoviePy v2 API
            final_video = final_video.with_audio(audio_clip)
            final_video = final_video.with_fps(self.fps)
        else:
            # MoviePy v1 API (fallback)
            final_video = final_video.set_audio(audio_clip)
            final_video = final_video.set_fps(self.fps)
        
        # Write video file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_video.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            bitrate=self.audio_bitrate,
            fps=self.fps,
            preset="medium"
        )
        
        # Clean up
        audio_clip.close()
        final_video.close()
        for clip in video_clips:
            clip.close()
        
        return output_path
