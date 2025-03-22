import json
import os
from typing import Dict
import openai
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPTS, get_content_plan_prompt
from .utils.logger import Logger

class ContentGenerator:
    def __init__(self, task_id: str):
        self._setup_llm()
        self.logger = Logger()
        self.task_id = task_id
        self.output_dir = os.path.join("data", self.task_id, "prompts")
        os.makedirs(self.output_dir, exist_ok=True)

    def _setup_llm(self):
        """Set up LLM connection."""
        # Load environment variables from .env file in project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(project_root)
        load_dotenv(os.path.join(project_root, '.env'))

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        self.client = openai.OpenAI()
    
    def generate_content(self, topic: str, detail: str, target_audience: str, mood: str) -> Dict:
        """Generate content plan for the given topic."""
        self.logger.section("Content Generation Started")
        self.logger.info(f"Topic: {topic}")
        self.logger.info(f"Detail: {detail}")
        self.logger.info(f"Target Audience: {target_audience}")
        self.logger.info(f"Mood: {mood}")
        
        # Generate new content plan system prompt
        prompt = get_content_plan_prompt(topic, detail, target_audience, mood)
        # Save prompt to file
        with open(os.path.join(self.output_dir, "content_plan_prompt.txt"), "w") as f: 
            f.write(prompt)
        # Log prompt
        self.logger.subsection("Prompt")
        self.logger.subsection(prompt)
        
        # Get LLM response
        self.logger.process("Requesting content generation from GPT-4...")
        response = self._get_llm_response(prompt)
        
        # Log response
        self.logger.subsection("Generated Content")
        self.logger.result("Content Plan", response)
        
        # Parse response into structured format
        self.logger.process("Parsing response...")
        content_plan = self._parse_llm_response(response)
        
        self.logger.success("Content generation completed successfully")
        return content_plan
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM."""
        self.logger.api_call("OpenAI", "Chat Completion", "Requesting content generation")
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["content_plan"]},
                {"role": "user", "content": prompt}
            ]
        )
        response_content = response.choices[0].message.content
        # Save response to file
        self._save_llm_response(response_content)
        return response_content
    
    def _save_llm_response(self, response: str):
        with open(os.path.join(self.output_dir, "content_plan_response.txt"), "w") as f:
            f.write(response)
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Convert LLM response into structured format."""
        try:
            # Convert JSON string to Python dictionary
            content_plan = json.loads(response)
            
            # Validate required fields
            required_fields = [
                "video_title", "video_description", "hook", "main_points",
                "conclusion", "overall_style_guide", "music_suggestion",
                "total_duration_seconds"
            ]
            
            for field in required_fields:
                if field not in content_plan:
                    raise ValueError(f"Missing required field: {field}")
            
            return content_plan
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            return self._generate_fallback_content()
        except Exception as e:
            self.logger.error(f"Error parsing response: {str(e)}")
            return self._generate_fallback_content()
    
    def _generate_fallback_content(self) -> Dict:
        """Generate fallback content when error occurs."""
        return {
            "video_title": "Error Occurred",
            "video_description": "An error occurred while generating content.",
            "hook": {
                "script": "Sorry, an error occurred.",
                "duration_seconds": 5,
                "image_keywords": ["error", "apology"],
                "visual_style": "Simple, minimalistic"
            },
            "main_points": [
                {
                    "title": "Error Occurred",
                    "script": "An error occurred while generating content.",
                    "duration_seconds": 8,
                    "image_keywords": ["error", "technical_difficulty"],
                    "visual_style": "Simple, minimalistic"
                }
            ],
            "conclusion": {
                "script": "We apologize for the inconvenience.",
                "duration_seconds": 5,
                "image_keywords": ["apology", "retry"],
                "visual_style": "Simple, minimalistic"
            },
            "overall_style_guide": {
                "art_style": "Minimalistic",
                "color_palette": ["#000000", "#FFFFFF", "#FF0000"],
                "mood_elements": ["simple", "clean"],
                "lighting": "Neutral",
                "composition": "Centered"
            },
            "music_suggestion": "Soft, apologetic background music",
            "total_duration_seconds": 30
        } 