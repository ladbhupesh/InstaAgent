"""API client wrappers with rate limiting and error handling."""

import os
import asyncio
from typing import Optional, List, Dict, Any
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from openai import AsyncOpenAI
from elevenlabs.client import ElevenLabs
import replicate

from .rate_limiter import RateLimiter, RateLimitConfig


class OpenAIClient:
    """OpenAI API client with rate limiting. Supports both OpenAI and Azure OpenAI."""
    
    def __init__(self):
        # Check if using Azure OpenAI
        use_azure = os.getenv("USE_AZURE_OPENAI", "false").lower() == "true"
        
        if use_azure:
            # Azure OpenAI configuration
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("AZURE_OPENAI_API_KEY not found in environment variables")
            
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            if not endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT not found in environment variables")
            
            # Ensure endpoint doesn't have trailing slash
            endpoint = endpoint.rstrip("/")
            # Azure OpenAI base URL format: https://{resource-name}.openai.azure.com/openai/deployments/{deployment}
            # We'll construct the full URL with deployment name for chat completions
            deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            if not deployment_name:
                raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME not found in environment variables")
            base_url = f"{endpoint}/openai/deployments/{deployment_name}"
            
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
            
            # Model deployment name (not model name) - already retrieved above
            self.model = deployment_name
            
            # For image generation, Azure uses a different deployment
            self.image_deployment = os.getenv("AZURE_OPENAI_IMAGE_DEPLOYMENT_NAME", self.model)
            
            # Azure OpenAI client configuration
            # For Azure, we need to include the deployment name in the base_url
            # and pass api-version as a query parameter
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=base_url,
                default_query={"api-version": api_version}
            )
            self.use_azure = True
            self.api_version = api_version
            self.azure_endpoint = endpoint
        else:
            # Standard OpenAI configuration
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
            self.use_azure = False
        
        # Rate limiter: 60 requests per minute
        self.rate_limiter = RateLimiter(
            RateLimitConfig(max_requests=60, time_window=60.0)
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """Generate text using OpenAI GPT models."""
        async with self.rate_limiter:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1792",  # Instagram Reels format (9:16)
        quality: str = "hd",
        n: int = 1
    ) -> List[str]:
        """Generate images using DALL-E 3."""
        async with self.rate_limiter:
            if self.use_azure:
                # For Azure OpenAI, image generation uses a different endpoint structure
                # Base URL should be: https://{endpoint}/openai/deployments/{deployment}
                image_base_url = f"{self.azure_endpoint}/openai/deployments/{self.image_deployment}"
                
                image_client = AsyncOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    base_url=image_base_url,
                    default_query={"api-version": self.api_version}
                )
                
                # Azure OpenAI: deployment name is used as model parameter
                # The SDK will append /images/generations to the base_url
                try:
                    response = await image_client.images.generate(
                        model=self.image_deployment,
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        n=n
                    )
                except Exception as e:
                    # If the above fails, try with the full endpoint path
                    image_base_url_full = f"{self.azure_endpoint}/openai/deployments/{self.image_deployment}/images/generations"
                    image_client = AsyncOpenAI(
                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        base_url=image_base_url_full,
                        default_query={"api-version": self.api_version}
                    )
                    response = await image_client.images.generate(
                        model=self.image_deployment,
                        prompt=prompt,
                        size=size,
                        quality=quality,
                        n=n
                    )
            else:
                # Standard OpenAI
                response = await self.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=n
                )
            
            return [image.url for image in response.data]


class ElevenLabsClient:
    """ElevenLabs API client for text-to-speech."""
    
    def __init__(self):
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
        
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_turbo_v2_5")
        
        # Rate limiter: 30 requests per minute
        self.rate_limiter = RateLimiter(
            RateLimitConfig(max_requests=30, time_window=60.0)
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def generate_speech(
        self,
        text: str,
        output_path: Optional[Path] = None,
        voice_id: Optional[str] = None
    ) -> bytes:
        """Generate speech audio from text."""
        async with self.rate_limiter:
            voice = voice_id or self.voice_id
            
            # Run synchronous ElevenLabs API in executor
            loop = asyncio.get_event_loop()
            
            def _generate():
                audio_generator = self.client.text_to_speech.convert(
                    voice_id=voice,
                    text=text,
                    model_id=self.model_id
                )
                
                audio_bytes = b""
                for chunk in audio_generator:
                    audio_bytes += chunk
                return audio_bytes
            
            audio_bytes = await loop.run_in_executor(None, _generate)
            
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(audio_bytes)
            
            return audio_bytes


class ReplicateClient:
    """Replicate API client for image generation (alternative to DALL-E)."""
    
    def __init__(self):
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables")
        
        self.client = replicate.Client(api_token=api_token)
        self.model = os.getenv(
            "REPLICATE_MODEL",
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b"
        )
        
        # Rate limiter: 20 requests per minute
        self.rate_limiter = RateLimiter(
            RateLimitConfig(max_requests=20, time_window=60.0)
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    async def generate_image(
        self,
        prompt: str,
        output_path: Optional[Path] = None,
        width: int = 1024,
        height: int = 1792
    ) -> str:
        """Generate image using Replicate."""
        async with self.rate_limiter:
            # Replicate runs synchronously, so we run it in executor
            loop = asyncio.get_event_loop()
            output = await loop.run_in_executor(
                None,
                lambda: self.client.run(
                    self.model,
                    input={
                        "prompt": prompt,
                        "width": width,
                        "height": height
                    }
                )
            )
            
            # Replicate returns a URL or list of URLs
            image_url = output[0] if isinstance(output, list) else output
            
            if output_path:
                # Download the image
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        image_data = await response.read()
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, "wb") as f:
                            f.write(image_data)
            
            return image_url
