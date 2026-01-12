"""Agent A: Trend & Concept Strategist - Generates high-engagement Reel concepts."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field

from utils.api_clients import OpenAIClient


class ReelConcept(BaseModel):
    """Structure for a Reel concept."""
    title: str = Field(description="Catchy title for the concept")
    hook: str = Field(description="Opening hook that grabs attention in first 3 seconds")
    value_proposition: str = Field(description="What value or insight the Reel provides")
    visual_style: str = Field(description="Description of visual style and aesthetic")
    target_audience: str = Field(description="Who this Reel is designed for")
    engagement_strategy: str = Field(description="How to maximize engagement (CTA, questions, etc.)")


class ConceptStrategist:
    """Agent A: Generates 3 distinct, high-engagement Instagram Reel concepts."""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
    
    async def generate_concepts(
        self,
        niche: str,
        keywords: str = "",
        additional_context: str = ""
    ) -> List[ReelConcept]:
        """
        Generate 3 distinct Reel concepts based on niche and keywords.
        
        Args:
            niche: The main niche or topic (e.g., "fitness", "cooking", "tech tips")
            keywords: Additional keywords to guide concept generation
            additional_context: Any additional context or requirements
        
        Returns:
            List of 3 ReelConcept objects
        """
        system_prompt = """You are an expert Instagram Reels strategist with deep knowledge of 
        viral content patterns, engagement psychology, and visual storytelling. Your task is to 
        create highly engaging Reel concepts that maximize viewer retention and interaction.
        
        Each concept should:
        1. Have a strong hook that captures attention in the first 3 seconds
        2. Provide clear value or entertainment
        3. Have a distinct visual style that stands out
        4. Include an engagement strategy (questions, CTAs, etc.)
        5. Be optimized for Instagram's algorithm (trending sounds, hashtags, etc.)
        
        Make each concept unique and different from the others."""
        
        user_prompt = f"""Generate 3 distinct, high-engagement Instagram Reel concepts for the niche: "{niche}"

        Keywords: {keywords if keywords else "None provided"}
        Additional Context: {additional_context if additional_context else "None"}
        
        For each concept, provide:
        1. Title: A catchy, searchable title
        2. Hook: An attention-grabbing opening (first 3 seconds) that makes viewers stop scrolling
        3. Value Proposition: What value, insight, or entertainment the Reel provides
        4. Visual Style: Detailed description of the visual aesthetic, colors, composition, and style
        5. Target Audience: Who this Reel is specifically designed for
        6. Engagement Strategy: How to maximize engagement (questions, CTAs, trending elements)
        
        Make sure each concept is:
        - Distinct from the others
        - Optimized for Instagram Reels format (9:16 vertical)
        - Designed for high engagement and shareability
        - Aligned with current trends in the niche
        
        IMPORTANT: You MUST respond with ONLY a valid JSON array. No explanations, no markdown, no code blocks.
        The response must start with [ and end with ].
        
        Format your response as a JSON array with exactly 3 objects, each containing:
        {{
            "title": "...",
            "hook": "...",
            "value_proposition": "...",
            "visual_style": "...",
            "target_audience": "...",
            "engagement_strategy": "..."
        }}
        
        Example format:
        [
            {{"title": "Example 1", "hook": "...", "value_proposition": "...", "visual_style": "...", "target_audience": "...", "engagement_strategy": "..."}},
            {{"title": "Example 2", "hook": "...", "value_proposition": "...", "visual_style": "...", "target_audience": "...", "engagement_strategy": "..."}},
            {{"title": "Example 3", "hook": "...", "value_proposition": "...", "visual_style": "...", "target_audience": "...", "engagement_strategy": "..."}}
        ]
        
        Respond with ONLY the JSON array, nothing else."""
        
        response = await self.openai_client.generate_text(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=2500
        )
        
        # Debug: Save raw response for troubleshooting
        import json
        import re
        
        # Log the raw response for debugging (first 500 chars)
        if len(response) > 500:
            print(f"Debug: Response preview: {response[:500]}...")
        else:
            print(f"Debug: Full response: {response}")
        
        try:
            # Extract JSON from response (handle markdown code blocks)
            cleaned_response = response.strip()
            
            # Remove markdown code blocks
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
            
            # Try to find JSON array in the response
            # Look for array pattern
            array_match = re.search(r'\[[\s\S]*\]', cleaned_response)
            if array_match:
                cleaned_response = array_match.group(0)
            
            # Fix escaped quotes (\" -> ")
            cleaned_response = cleaned_response.replace('\\"', '"')
            # Also handle other common escape sequences
            cleaned_response = cleaned_response.replace('\\n', '\n')
            cleaned_response = cleaned_response.replace('\\t', '\t')
            
            # Try to parse JSON
            concepts_data = json.loads(cleaned_response)
            
            # Validate and create ReelConcept objects
            concepts = []
            for concept_data in concepts_data:
                if isinstance(concept_data, dict):
                    try:
                        concepts.append(ReelConcept(**concept_data))
                    except Exception as e:
                        print(f"Warning: Skipping invalid concept: {e}")
                        continue
            
            if len(concepts) != 3:
                raise ValueError(f"Expected 3 concepts, got {len(concepts)}")
            
            return concepts
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: try to extract concepts using LLM again with stricter format
            fallback_prompt = f"""The previous response was not in the correct format. 
            Please provide ONLY a valid JSON array with exactly 3 objects, no other text.
            
            {user_prompt}
            
            Respond with ONLY the JSON array, nothing else."""
            
            response = await self.openai_client.generate_text(
                prompt=fallback_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=2000
            )
            
            # Clean and parse fallback response
            cleaned_response = response.strip()
            
            # Remove markdown code blocks
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
            
            # Try to find JSON array
            array_match = re.search(r'\[[\s\S]*\]', cleaned_response)
            if array_match:
                cleaned_response = array_match.group(0)
            
            # Fix escaped quotes
            cleaned_response = cleaned_response.replace('\\"', '"')
            cleaned_response = cleaned_response.replace('\\n', '\n')
            cleaned_response = cleaned_response.replace('\\t', '\t')
            
            if cleaned_response.startswith("["):
                try:
                    concepts_data = json.loads(cleaned_response)
                    concepts = []
                    for c in concepts_data:
                        if isinstance(c, dict):
                            try:
                                concepts.append(ReelConcept(**c))
                            except Exception:
                                continue
                    if len(concepts) == 3:
                        return concepts
                except json.JSONDecodeError:
                    pass
            
            # If we still can't parse, try one more time with more aggressive cleaning
            try:
                # Remove any text before first [
                start_idx = cleaned_response.find('[')
                if start_idx >= 0:
                    cleaned_response = cleaned_response[start_idx:]
                    # Find matching closing bracket
                    bracket_count = 0
                    end_idx = -1
                    for i, char in enumerate(cleaned_response):
                        if char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                end_idx = i + 1
                                break
                    if end_idx > 0:
                        cleaned_response = cleaned_response[:end_idx]
                        concepts_data = json.loads(cleaned_response)
                        concepts = []
                        for c in concepts_data:
                            if isinstance(c, dict):
                                try:
                                    concepts.append(ReelConcept(**c))
                                except Exception:
                                    continue
                        if len(concepts) >= 1:  # Accept at least 1 concept
                            print(f"Warning: Generated {len(concepts)} concepts instead of 3")
                            return concepts
            except Exception:
                pass
            
            # If we still can't parse, raise with more context
            raise ValueError(
                f"Failed to parse concepts from response. "
                f"Original error: {str(e)}. "
                f"Response length: {len(response)} chars. "
                f"Response preview: {response[:500]}..."
            )
