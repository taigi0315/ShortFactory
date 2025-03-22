import json
import os
from typing import Dict, Optional
from dataclasses import dataclass
import openai

@dataclass
class PromptConfig:
    story: str
    mood: str
    style: str
    target_audience: str

class PromptGenerator:
    def __init__(self):
        self.storage_path = "data/prompts.json"
        self._ensure_storage_exists()
        self._setup_llm()
    
    def _ensure_storage_exists(self):
        """Ensure local storage directory and file exist."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)
    
    def _setup_llm(self):
        """Setup LLM connection."""
        self.client = openai.OpenAI()
    
    def generate_content_prompt(self, topic: str, target_audience: str, mood: str) -> str:
        """Generate a prompt for content creation."""
        return f"""
Create a comprehensive content plan for a YouTube Short video about {topic}.

Target audience: {target_audience}
Mood: {mood}

Please provide a structured plan with the following sections:

1. Story Overview
   - Main narrative that ties all scenes together
   - Hook (attention-grabbing opening)
   - Key message or takeaway
   - Call to action

2. Scene Breakdown
   For each scene, provide:
   - Scene ID and description
   - Action elements (specific movements/transitions)
   - Visual style and composition
   - Narration script with emphasis markers
   - Duration
   - Sound effects and background music notes

3. Visual Elements
   - Style guide for each scene
   - Color palette
   - Camera angles and movements
   - Text overlay design
   - Animation specifications

4. Audio Elements
   - Background music style and mood
   - Sound effect placement
   - Voice-over tone and pacing
   - Audio mixing instructions

5. Educational Components (if applicable)
   - Key vocabulary
   - Learning objectives
   - Visual demonstrations
   - Interactive elements

6. Engagement Elements
   - Attention-grabbing moments
   - Viewer interaction points
   - Share-worthy moments
   - Call-to-action placement

Make the content engaging, educational, and suitable for short-form video content.
Focus on visual appeal and viewer retention.
"""
    
    def generate_image_prompt(self, scene_description: Dict) -> str:
        """Generate a prompt for AI image generation based on scene description."""
        return f"""
Create a detailed image generation prompt for this scene:

Scene Description: {scene_description['description']}
Style: {scene_description['image']['style']}
Main Element: {scene_description['image']['main_element']}
Composition: {scene_description['image']['composition']}
Background: {scene_description['image']['background_scene']}
Color Palette: {scene_description['image']['color_palette']}

The prompt should be detailed and specific, suitable for AI image generation.
Focus on:
1. Visual composition and framing
2. Lighting and atmosphere
3. Color scheme and mood
4. Main subject details
5. Background elements
6. Text placement (if applicable)
"""
    
    def generate_video_prompt(self, scene_description: Dict) -> str:
        """Generate a prompt for AI video generation based on scene description."""
        return f"""
Create a detailed video generation prompt for this scene:

Scene Description: {scene_description['description']}
Duration: {scene_description['duration']} seconds
Style: {scene_description['image']['style']}
Main Element: {scene_description['image']['main_element']}
Animation: {scene_description['animation_instructions']}

The prompt should be detailed and specific, suitable for AI video generation.
Include:
1. Scene composition and camera movements
2. Animation sequence
3. Transitions and effects
4. Timing and pacing
5. Visual style consistency
6. Text animation (if applicable)
"""
    
    def generate_search_query(self, scene_description: Dict) -> str:
        """Generate a search query for web image search."""
        return f"""
Create a search query to find relevant images for this scene:

Scene Description: {scene_description['description']}
Style: {scene_description['image']['style']}
Main Element: {scene_description['image']['main_element']}
Mood: {scene_description['mood']}

The query should be optimized for stock photo/video websites.
Focus on:
1. Main subject
2. Visual style
3. Mood and atmosphere
4. Technical specifications
"""
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM."""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional content creator specializing in visual prompts."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    def _get_cached_prompt(self, prompt_type: str, config: PromptConfig) -> Optional[str]:
        """Get cached prompt if it exists."""
        prompts = self._load_prompts()
        key = self._create_cache_key(prompt_type, config)
        return prompts.get(key)
    
    def _cache_prompt(self, prompt_type: str, config: PromptConfig, prompt: str):
        """Cache the generated prompt."""
        prompts = self._load_prompts()
        key = self._create_cache_key(prompt_type, config)
        prompts[key] = prompt
        self._save_prompts(prompts)
    
    def _create_cache_key(self, prompt_type: str, config: PromptConfig) -> str:
        """Create a cache key for the prompt."""
        return f"{prompt_type}_{hash(config.story)}_{config.mood}_{config.style}_{config.target_audience}"
    
    def _load_prompts(self) -> Dict:
        """Load saved prompts."""
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def _save_prompts(self, prompts: Dict):
        """Save prompts."""
        with open(self.storage_path, 'w') as f:
            json.dump(prompts, f, indent=2) 