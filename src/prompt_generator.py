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
    
    def generate_image_prompt(self, story: str, mood: str, style: str, 
                            target_audience: str) -> str:
        """Generate a prompt for AI image generation."""
        config = PromptConfig(story, mood, style, target_audience)
        
        # Check cache
        cached_prompt = self._get_cached_prompt("image", config)
        if cached_prompt:
            return cached_prompt
        
        # Generate new prompt
        prompt = self._create_image_prompt(config)
        response = self._get_llm_response(prompt)
        
        # Cache the result
        self._cache_prompt("image", config, response)
        
        return response
    
    def generate_video_prompt(self, story: str, mood: str, style: str,
                            target_audience: str) -> str:
        """Generate a prompt for AI video generation."""
        config = PromptConfig(story, mood, style, target_audience)
        
        # Check cache
        cached_prompt = self._get_cached_prompt("video", config)
        if cached_prompt:
            return cached_prompt
        
        # Generate new prompt
        prompt = self._create_video_prompt(config)
        response = self._get_llm_response(prompt)
        
        # Cache the result
        self._cache_prompt("video", config, response)
        
        return response
    
    def generate_search_query(self, story: str, mood: str, 
                            target_audience: str) -> str:
        """Generate a search query for web image search."""
        config = PromptConfig(story, mood, "realistic", target_audience)
        
        # Check cache
        cached_prompt = self._get_cached_prompt("search", config)
        if cached_prompt:
            return cached_prompt
        
        # Generate new prompt
        prompt = self._create_search_prompt(config)
        response = self._get_llm_response(prompt)
        
        # Cache the result
        self._cache_prompt("search", config, response)
        
        return response
    
    def _create_image_prompt(self, config: PromptConfig) -> str:
        """Create a prompt for image generation."""
        return f"""
Create a detailed prompt for generating an image that matches this story:
{config.story}

Target audience: {config.target_audience}
Mood: {config.mood}
Style: {config.style}

The prompt should be detailed and specific, suitable for AI image generation.
Focus on visual elements, composition, lighting, and atmosphere.
"""
    
    def _create_video_prompt(self, config: PromptConfig) -> str:
        """Create a prompt for video generation."""
        return f"""
Create a detailed prompt for generating a video that matches this story:
{config.story}

Target audience: {config.target_audience}
Mood: {config.mood}
Style: {config.style}

The prompt should be detailed and specific, suitable for AI video generation.
Include information about:
- Scene composition
- Camera movements
- Transitions
- Visual effects
- Timing and pacing
"""
    
    def _create_search_prompt(self, config: PromptConfig) -> str:
        """Create a prompt for web image search."""
        return f"""
Create a search query to find images that match this story:
{config.story}

Target audience: {config.target_audience}
Mood: {config.mood}

The query should be specific and focused on finding relevant, high-quality images.
Include key visual elements and descriptive terms.
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