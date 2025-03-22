import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class VisualSource(Enum):
    WEB_SEARCH = "web_search"
    AI_IMAGE = "ai_image"
    AI_VIDEO = "ai_video"

@dataclass
class VisualAsset:
    type: str  # gameplay, static, animation
    content: str
    timing: float  # start time in seconds
    style: str
    duration: float  # duration in seconds
    source_type: VisualSource
    source_url: Optional[str] = None

class VisualSelector:
    def __init__(self):
        self.storage_path = "data/visuals.json"
        self._ensure_storage_exists()
        self.prompt_generator = None  # Will be initialized when needed
    
    def _ensure_storage_exists(self):
        """Ensure local storage directory and file exist."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)
    
    def _load_visuals(self) -> Dict:
        """Load saved visual assets."""
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def _save_visuals(self, visuals: Dict):
        """Save visual assets."""
        with open(self.storage_path, 'w') as f:
            json.dump(visuals, f, indent=2)
    
    def select_visuals(self, script: str) -> List[Dict]:
        """Select visual assets based on the script."""
        visuals = self._load_visuals()
        
        # Use script hash as key
        script_key = str(hash(script))
        
        if script_key in visuals:
            return visuals[script_key]
        
        # Generate new visual assets
        new_visuals = self._create_visuals_for_script(script)
        
        # Save visual assets
        visuals[script_key] = new_visuals
        self._save_visuals(visuals)
        
        return new_visuals
    
    def _create_visuals_for_script(self, script: str) -> List[Dict]:
        """Generate visual assets based on the script."""
        sections = script.split("\n\n")
        visuals = []
        current_time = 0.0
        
        for section in sections:
            if "[HOOK]" in section:
                # Determine the best visual source for the hook
                source_type = self._determine_visual_type(section, "hook")
                visual = self._get_visual_from_source(section, source_type, current_time, 3.0)
                visuals.append(visual)
                current_time += 3.0
            
            elif "[CONTENT]" in section:
                # Visual assets for each content point
                points = [line.strip() for line in section.split("\n") if line.strip() and not line.startswith("[")]
                for point in points:
                    source_type = self._determine_visual_type(point, "content")
                    visual = self._get_visual_from_source(point, source_type, current_time, 4.0)
                    visuals.append(visual)
                    current_time += 4.0
            
            elif "[CONCLUSION]" in section:
                source_type = self._determine_visual_type(section, "conclusion")
                visual = self._get_visual_from_source(section, source_type, current_time, 3.0)
                visuals.append(visual)
        
        return visuals
    
    def _determine_visual_type(self, content: str, section_type: str) -> VisualSource:
        """Determine the best visual source type for the content."""
        # This is a simplified decision logic. In production, you would:
        # 1. Analyze content complexity
        # 2. Consider available resources
        # 3. Check content type (static vs dynamic)
        # 4. Consider performance requirements
        
        if section_type == "hook":
            return VisualSource.AI_VIDEO  # Dynamic content for attention
        elif section_type == "content":
            # Alternate between different sources for variety
            return VisualSource.AI_IMAGE
        else:  # conclusion
            return VisualSource.WEB_SEARCH  # Use existing assets for conclusion
    
    def _get_visual_from_source(self, content: str, source_type: VisualSource,
                              timing: float, duration: float) -> Dict:
        """Get visual asset from the appropriate source."""
        if self.prompt_generator is None:
            from .prompt_generator import PromptGenerator
            self.prompt_generator = PromptGenerator()
        
        if source_type == VisualSource.AI_IMAGE:
            prompt = self.prompt_generator.generate_image_prompt(
                content, "engaging", "modern", "general"
            )
            # In production, you would call the actual AI image generation service
            return {
                "type": "static",
                "content": prompt,
                "timing": timing,
                "style": "modern",
                "duration": duration,
                "source_type": source_type.value,
                "source_url": None  # Will be populated when image is generated
            }
        
        elif source_type == VisualSource.AI_VIDEO:
            prompt = self.prompt_generator.generate_video_prompt(
                content, "dynamic", "modern", "general"
            )
            # In production, you would call the actual AI video generation service
            return {
                "type": "video",
                "content": prompt,
                "timing": timing,
                "style": "modern",
                "duration": duration,
                "source_type": source_type.value,
                "source_url": None  # Will be populated when video is generated
            }
        
        else:  # WEB_SEARCH
            query = self.prompt_generator.generate_search_query(
                content, "engaging", "general"
            )
            # In production, you would call the actual web search service
            return {
                "type": "static",
                "content": query,
                "timing": timing,
                "style": "realistic",
                "duration": duration,
                "source_type": source_type.value,
                "source_url": None  # Will be populated when image is found
            } 