"""Agent E: Caption Generator - Creates engaging Instagram captions with hashtags."""

from typing import Dict, List
from pydantic import BaseModel, Field

from utils.api_clients import OpenAIClient


class InstagramCaption(BaseModel):
    """Structure for an Instagram post caption."""
    caption: str = Field(description="Main caption text (engaging, concise, optimized for engagement)")
    hashtags: List[str] = Field(description="List of relevant hashtags (15-30 hashtags)")
    full_caption: str = Field(description="Complete caption with hashtags formatted for Instagram")


class CaptionGenerator:
    """Agent E: Generates engaging Instagram captions with relevant hashtags."""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    async def generate_caption(
        self,
        concept: Dict,
        script: Dict,
        niche: str,
        keywords: str = ""
    ) -> InstagramCaption:
        """
        Generate an engaging Instagram caption with hashtags.
        
        Args:
            concept: The selected ReelConcept (as dict)
            script: The generated ReelScript (as dict)
            niche: The main niche or topic
            keywords: Additional keywords
        
        Returns:
            InstagramCaption object with caption and hashtags
        """
        system_prompt = """You are an expert Instagram content strategist specializing in creating 
        high-engagement captions and hashtag strategies. Your captions maximize reach, engagement, 
        and follower growth.
        
        CRITICAL CONTENT GUIDELINES:
        - ALL captions must be FUNNY, JOYFUL, and POSITIVE
        - NO negative energy, drama, conflict, or toxic themes
        - Focus on humor, lightheartedness, and uplifting messages
        - Make readers laugh, smile, and feel good
        - Use playful, cheerful, and optimistic tones
        - Avoid any content that could bring down the mood
        
        Your captions should:
        1. Start with a hook that complements the video content (funny, joyful, or positive)
        2. Be concise but engaging (Instagram captions work best at 125-150 characters for optimal engagement)
        3. Include a clear call-to-action (CTA) that's fun and positive
        4. Use emojis strategically (2-4 emojis max) - prefer happy, fun emojis
        5. Have natural line breaks for readability
        6. Match the tone and style of the video content (always positive, funny, or joyful)
        7. Always maintain a lighthearted, cheerful, and uplifting tone - never negative
        
        Your hashtag strategy should:
        1. Include 15-30 relevant hashtags
        2. Mix popular hashtags (100K-1M posts) with niche-specific ones
        3. Include trending hashtags in the niche
        4. Use a mix of broad and specific hashtags
        5. Include branded/community hashtags when relevant
        6. Avoid banned or spammy hashtags
        
        Format hashtags as a list without the # symbol (we'll add it)."""
        
        concept_str = f"""
        Title: {concept.get('title', 'N/A')}
        Hook: {concept.get('hook', 'N/A')}
        Value Proposition: {concept.get('value_proposition', 'N/A')}
        Target Audience: {concept.get('target_audience', 'N/A')}
        """
        
        script_summary = script.get('full_transcript', '')
        hook_enhancement = script.get('hook_enhancement', '')
        
        user_prompt = f"""Create an engaging Instagram caption with hashtags for this Reel:

        Concept:
        {concept_str}
        
        Script Summary: {script_summary[:500]}...
        Hook: {hook_enhancement}
        
        Niche: {niche}
        Keywords: {keywords if keywords else "None provided"}
        
        IMPORTANT: The caption MUST be funny, joyful, and positive. NO negative energy, drama, 
        or toxic themes. Focus on humor, lightheartedness, and making people laugh and feel good.
        Use cheerful, playful, and optimistic language throughout.
        
        Create:
        1. A compelling caption (125-150 characters ideal, max 2200 characters)
           - Start with a hook that complements the video
           - Include value or insight
           - Add a clear CTA (like, comment, save, follow)
           - Use 2-4 strategic emojis
           - Use line breaks for readability
        
        2. A list of 15-30 relevant hashtags
           - Mix popular and niche hashtags
           - Include trending hashtags in this niche
           - Use both broad and specific hashtags
           - Ensure they're relevant to the content
        
        3. Format the full caption (caption + hashtags separated by line breaks)
        
        Format your response as JSON:
        {{
            "caption": "Main caption text here...",
            "hashtags": ["hashtag1", "hashtag2", "hashtag3", ...],
            "full_caption": "Caption text\\n\\n#hashtag1 #hashtag2 #hashtag3 ..."
        }}
        
        IMPORTANT: 
        - Hashtags in the list should NOT include the # symbol
        - The full_caption should have hashtags WITH # symbols
        - Use \\n for line breaks in the full_caption
        - Make sure hashtags are relevant and not banned/spammy"""
        
        response = await self.openai_client.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse JSON response
        import json
        try:
            # Extract JSON from response
            cleaned_response = response.strip()
            
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
            
            caption_data = json.loads(cleaned_response)
            
            # Ensure hashtags are formatted correctly
            hashtags = caption_data.get("hashtags", [])
            # Remove # if present in hashtags list
            hashtags = [tag.lstrip("#") for tag in hashtags]
            
            # Build full caption if not provided or incomplete
            caption_text = caption_data.get("caption", "")
            if not caption_data.get("full_caption"):
                hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
                full_caption = f"{caption_text}\n\n{hashtag_str}"
            else:
                # Convert escaped newlines to actual newlines
                full_caption = caption_data.get("full_caption", "").replace("\\n", "\n")
            
            caption = InstagramCaption(
                caption=caption_text,
                hashtags=hashtags,
                full_caption=full_caption
            )
            
            return caption
            
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
                max_tokens=1000
            )
            
            cleaned_response = response.strip()
            if cleaned_response.startswith("{"):
                caption_data = json.loads(cleaned_response)
                hashtags = [tag.lstrip("#") for tag in caption_data.get("hashtags", [])]
                caption_text = caption_data.get("caption", "")
                if not caption_data.get("full_caption"):
                    hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
                    full_caption = f"{caption_text}\n\n{hashtag_str}"
                else:
                    # Convert escaped newlines to actual newlines
                    full_caption = caption_data.get("full_caption", "").replace("\\n", "\n")
                
                caption = InstagramCaption(
                    caption=caption_text,
                    hashtags=hashtags,
                    full_caption=full_caption
                )
                return caption
            
            raise ValueError(f"Failed to parse caption from response: {e}")
