"""Configuration management for the application."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Azure OpenAI (Primary)
    use_azure_openai: bool = True
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_openai_deployment_name: Optional[str] = None
    azure_openai_image_deployment_name: Optional[str] = None
    
    # Standard OpenAI (Alternative)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    
    # ElevenLabs
    elevenlabs_api_key: str
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_model_id: str = "eleven_turbo_v2_5"
    
    # Replicate (optional)
    replicate_api_token: Optional[str] = None
    replicate_model: str = "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
    
    # Image Generation
    image_generation_provider: str = "openai"  # openai or replicate
    
    # State Management
    state_storage_path: Path = Path("./state")
    state_file_format: str = "json"
    
    # Rate Limiting
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    rate_limit_requests_per_minute: int = 60
    
    # Video Configuration
    video_resolution: str = "1080x1920"
    video_fps: int = 30
    audio_bitrate: str = "192k"
    
    # Output
    output_dir: Path = Path("./output")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    try:
        return Settings()
    except Exception as e:
        raise ValueError(
            f"Failed to load settings. Please check your .env file. Error: {e}"
        )
