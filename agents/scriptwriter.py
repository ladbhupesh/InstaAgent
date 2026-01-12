"""Agent B: Scriptwriter & Prompt Engineer - Creates scripts and image prompts."""

from typing import List, Dict
from pydantic import BaseModel, Field

from utils.api_clients import OpenAIClient


class ScriptSegment(BaseModel):
    """A segment of the script with corresponding visual prompt."""
    segment_number: int = Field(description="Order of this segment in the script")
    spoken_text: str = Field(description="Text to be spoken in this segment")
    image_prompt: str = Field(description="Detailed DALL-E/Midjourney style prompt for the visual")
    duration_estimate: float = Field(description="Estimated duration in seconds for this segment")
    visual_description: str = Field(description="Description of what should be shown visually")


class ReelScript(BaseModel):
    """Complete script with all segments."""
    full_transcript: str = Field(description="Complete spoken transcript")
    segments: List[ScriptSegment] = Field(description="Segmented script with visual prompts")
    total_duration: float = Field(description="Total estimated duration in seconds")
    hook_enhancement: str = Field(description="Enhanced hook for maximum engagement")
    pacing_notes: str = Field(description="Notes on pacing and timing")


class Scriptwriter:
    """Agent B: Creates optimized scripts and sequential image generation prompts."""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    async def generate_script(
        self,
        concept: Dict,
        target_duration: float = 30.0,
        style_preference: str = ""
    ) -> ReelScript:
        """
        Generate a complete script with image prompts based on a selected concept.
        
        Args:
            concept: The selected ReelConcept (as dict)
            target_duration: Target duration in seconds (default 30 for Reels)
            style_preference: Additional style preferences for visuals
        
        Returns:
            ReelScript object with transcript and image prompts
        """
        system_prompt = """You are an expert scriptwriter and visual prompt engineer specializing 
        in Instagram Reels. You create engaging, concise scripts optimized for viewer retention 
        and generate detailed image generation prompts that perfectly match the script content.
        
        CRITICAL CONTENT GUIDELINES:
        - ALL content must be FUNNY, JOYFUL, and POSITIVE
        - NO negative energy, drama, conflict, or toxic themes
        - Focus on humor, lightheartedness, and uplifting moments
        - Make viewers laugh, smile, and feel good
        - Use playful, cheerful, and optimistic tones throughout
        - Avoid any content that could bring down the mood or create negative feelings
        
        Your scripts should:
        1. Start with a strong hook (first 3 seconds) that's funny or joyful
        2. Maintain engagement through humor, positivity, and entertainment
        3. Be optimized for spoken delivery (natural pauses, emphasis, comedic timing)
        4. Match the target duration precisely
        5. Include clear visual transitions
        6. Always maintain a positive, funny, or joyful tone - never negative or dramatic
        
        Your image prompts should:
        1. Be simple, pleasant, and clean - NOT fancy, complex, or heavy
        2. Match the spoken content at each moment (with positive, cheerful visuals)
        3. Be optimized for vertical 9:16 format
        4. Use soft, natural lighting and pleasant colors (not overly dramatic or intense)
        5. Create visual continuity between segments
        6. Keep visuals light, simple, and easy on the eyes - avoid heavy effects, complex compositions, or overwhelming details
        7. Focus on pleasant, clean aesthetics - simple backgrounds, natural expressions, minimal but effective visuals
        8. Avoid overly stylized, dramatic, or complex imagery - prefer simplicity and pleasantness"""
        
        concept_str = f"""
        Title: {concept.get('title', 'N/A')}
        Hook: {concept.get('hook', 'N/A')}
        Value Proposition: {concept.get('value_proposition', 'N/A')}
        Visual Style: {concept.get('visual_style', 'N/A')}
        Target Audience: {concept.get('target_audience', 'N/A')}
        Engagement Strategy: {concept.get('engagement_strategy', 'N/A')}
        """
        
        user_prompt = f"""Create a complete Instagram Reels script based on this concept:

        {concept_str}
        
        Requirements:
        - Target duration: {target_duration} seconds
        - Format: Vertical 9:16 (Instagram Reels)
        - Style preference: {style_preference if style_preference else "Match the concept's visual style"}
        - CRITICAL: Keep the script funny, joyful, and positive. NO negative energy, drama, or 
          toxic themes. Focus on humor, lightheartedness, and making viewers laugh and feel good.
        
        Create:
        1. A full spoken transcript optimized for engagement and natural delivery
        2. Break the script into 4-8 segments (each segment should have a corresponding visual)
        3. For each segment, provide:
           - The spoken text for that segment
           - A detailed image generation prompt (DALL-E 3/Midjourney style) that matches the visual
           - Estimated duration for that segment
           - Visual description
        
        4. An enhanced hook that maximizes the first 3 seconds
        5. Pacing notes for optimal delivery
        
        The image prompts should be:
        - Simple, pleasant, and clean - NOT fancy or heavy
        - Include soft, natural lighting and pleasant colors
        - Optimized for vertical format
        - Create visual storytelling that matches the script
        - Each prompt should be distinct but maintain visual continuity
        - Keep visuals light and easy on the eyes - avoid complex compositions, heavy effects, or overwhelming details
        - Focus on simplicity, pleasantness, and clean aesthetics
        - Use natural, soft colors and simple backgrounds
        - Avoid overly stylized, dramatic, or complex imagery
        
        Format your response as JSON:
        {{
            "full_transcript": "Complete transcript here...",
            "hook_enhancement": "Enhanced hook for first 3 seconds...",
            "pacing_notes": "Notes on pacing...",
            "total_duration": {target_duration},
            "segments": [
                {{
                    "segment_number": 1,
                    "spoken_text": "Text for this segment...",
                    "image_prompt": "Detailed DALL-E style prompt...",
                    "duration_estimate": 3.5,
                    "visual_description": "What should be shown..."
                }},
                ...
            ]
        }}"""
        
        response = await self.openai_client.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3000
        )
        
        # Parse JSON response
        import json
        try:
            # Extract JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            script_data = json.loads(response)
            
            # Create segments
            segments = [
                ScriptSegment(**seg) for seg in script_data.get("segments", [])
            ]
            
            # Create ReelScript
            script = ReelScript(
                full_transcript=script_data.get("full_transcript", ""),
                segments=segments,
                total_duration=script_data.get("total_duration", target_duration),
                hook_enhancement=script_data.get("hook_enhancement", ""),
                pacing_notes=script_data.get("pacing_notes", "")
            )
            
            return script
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback parsing
            fallback_prompt = f"""The previous response was not in valid JSON format.
            Please provide ONLY a valid JSON object, no other text.
            
            {user_prompt}
            
            Respond with ONLY the JSON object, nothing else."""
            
            response = await self.openai_client.generate_text(
                prompt=fallback_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=3000
            )
            
            response = response.strip()
            if response.startswith("{"):
                script_data = json.loads(response)
                segments = [ScriptSegment(**seg) for seg in script_data.get("segments", [])]
                script = ReelScript(
                    full_transcript=script_data.get("full_transcript", ""),
                    segments=segments,
                    total_duration=script_data.get("total_duration", target_duration),
                    hook_enhancement=script_data.get("hook_enhancement", ""),
                    pacing_notes=script_data.get("pacing_notes", "")
                )
                return script
            
            raise ValueError(f"Failed to parse script from response: {e}")
