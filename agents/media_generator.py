"""Agent C: Media Generator - Generates images using AI."""

import asyncio
from pathlib import Path
from typing import List, Optional
import os

from utils.api_clients import OpenAIClient, ReplicateClient


class MediaGenerator:
    """Agent C: Generates high-quality images from prompts."""
    
    def __init__(self):
        provider = os.getenv("IMAGE_GENERATION_PROVIDER", "openai").lower()
        
        if provider == "openai":
            self.client = OpenAIClient()
            self.use_replicate = False
        elif provider == "replicate":
            self.client = ReplicateClient()
            self.use_replicate = True
        else:
            raise ValueError(f"Unknown image generation provider: {provider}")
    
    async def generate_images(
        self,
        image_prompts: List[str],
        output_dir: Path,
        prefix: str = "image"
    ) -> List[Path]:
        """
        Generate images from a list of prompts.
        
        Args:
            image_prompts: List of detailed image generation prompts
            output_dir: Directory where images will be saved
            prefix: Prefix for image filenames
        
        Returns:
            List of paths to generated image files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        image_paths = []
        
        # Generate images concurrently (with rate limiting handled by clients)
        tasks = []
        for i, prompt in enumerate(image_prompts):
            output_path = output_dir / f"{prefix}_{i+1:02d}.png"
            tasks.append(self._generate_single_image(prompt, output_path, i))
        
        # Execute with some concurrency control
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Extract the actual exception from RetryError or other wrapped exceptions
                actual_error = result
                try:
                    # Handle tenacity RetryError
                    if hasattr(result, 'last_attempt'):
                        last_attempt = result.last_attempt
                        if hasattr(last_attempt, 'exception') and last_attempt.exception():
                            actual_error = last_attempt.exception()
                        elif hasattr(last_attempt, 'result') and isinstance(last_attempt.result(), Exception):
                            actual_error = last_attempt.result()
                    # Handle other wrapped exceptions
                    elif hasattr(result, 'args') and result.args:
                        if isinstance(result.args[0], Exception):
                            actual_error = result.args[0]
                except Exception:
                    pass  # Use the original error if extraction fails
                
                error_msg = str(actual_error)
                error_type = type(actual_error).__name__
                print(f"Error generating image {i+1}: {error_type}: {error_msg}")
                # Continue with other images
            elif result:
                image_paths.append(result)
        
        if not image_paths:
            raise RuntimeError(
                "Failed to generate any images. Please check your API configuration and try again."
            )
        
        return sorted(image_paths)
    
    async def _generate_single_image(
        self,
        prompt: str,
        output_path: Path,
        index: int
    ) -> Optional[Path]:
        """Generate a single image from a prompt."""
        try:
            if self.use_replicate:
                # Replicate client
                image_url = await self.client.generate_image(
                    prompt=prompt,
                    output_path=output_path
                )
            else:
                # OpenAI DALL-E 3
                image_urls = await self.client.generate_image(
                    prompt=prompt,
                    size="1024x1792",  # Instagram Reels format
                    quality="hd",
                    n=1
                )
                
                if image_urls:
                    # Download the image
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(image_urls[0]) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                with open(output_path, "wb") as f:
                                    f.write(image_data)
                            else:
                                raise Exception(f"Failed to download image: {response.status}")
            
            if output_path.exists():
                print(f"Generated image {index+1}: {output_path.name}")
                return output_path
            else:
                raise Exception(f"Image file was not created: {output_path}")
                
        except Exception as e:
            print(f"Error generating image {index+1}: {e}")
            return None
