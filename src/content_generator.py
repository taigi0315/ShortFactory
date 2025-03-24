import json
import os
from typing import Dict, Any
import openai
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPTS, get_content_plan_prompt
from .utils.logger import Logger
from google import genai


class ContentGenerator:
    def __init__(self, task_id: str, model: str):
        self.task_id = task_id
        self.model = model
        self.logger = Logger()
        self._setup_llm()
        self.output_dir = os.path.join("data", self.task_id, "prompts")
        os.makedirs(self.output_dir, exist_ok=True)

    def _setup_llm(self):
        """Set up LLM connection."""
        # Load environment variables from .env file in project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(project_root)
        load_dotenv(os.path.join(project_root, '.env'))

        
        if self.model == "gemini":
            self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        else:
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError(
                    "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                    "in your .env file or system environment variables."
                )
            self.client = openai.OpenAI()
    
    def generate_content(self, topic: str, detail: str, target_audience: str, mood: str, image_style: str) -> Dict:
        """Generate content plan for the given topic."""
        self.logger.section("Content Generation Started")
        self.logger.info(f"Topic: {topic}")
        self.logger.info(f"Detail: {detail}")
        self.logger.info(f"Target Audience: {target_audience}")
        self.logger.info(f"Mood: {mood}")
        self.logger.info(f"Image Style: {image_style}")

        # Generate new content plan system prompt
        system_prompt = get_content_plan_prompt(topic, detail, target_audience, mood, image_style)
        # Save prompt to file
        with open(os.path.join(self.output_dir, "content_plan_prompt.txt"), "w") as f: 
            f.write(system_prompt)
        # Log prompt
        self.logger.subsection("Prompt")
        self.logger.subsection(system_prompt)
        
        # Get LLM response
        self.logger.process(f"Requesting content generation from {self.model}")
        response = self._get_llm_response(system_prompt)
        
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
        if self.model == "gemini":
            response_content = self._get_llm_response_gemini(prompt)
        elif self.model == "gpt-4o":
            response_content = self._get_llm_response_gpt4o(prompt)
        else:
            raise ValueError(f"Invalid model: {self.model}")

        # Save response to file
        self._save_llm_response(response_content)
        return response_content

    def _get_llm_response_gemini(self, prompt: str) -> str:
        self.logger.api_call("Google", "Gemini", "Requesting content generation")
        response = self.client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        # 응답 텍스트 추출
        response_text = response.candidates[0].content.parts[0].text
        print(f"response_text: {response_text}")
        # JSON 형식으로 변환
        try:
            # 마크다운 코드 블록 제거
            response_text = response_text.replace("```json", "").replace("```", "")
            # JSON 형식 검증
            # json.loads(response_text)
            print(f"response_text after: {response_text}")
            return response_text
        except json.JSONDecodeError as e:
            self.logger.error(f"Error converting response to JSON: {str(e)}")
            return None
    
    def _get_llm_response_gpt4o(self, prompt: str) -> str:
        self.logger.api_call("OpenAI", "Chat Completion", "Requesting content generation")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def _save_llm_response(self, response: str):
        with open(os.path.join(self.output_dir, "content_plan_response.txt"), "w") as f:
            f.write(response)
    
    def _parse_llm_response(self, response: str) -> Dict:
        """Convert LLM response into structured format."""
        try:
            # Convert JSON string to Python dictionary
            print(f"PARSE LLM RESPONSE")
            print(f"response: {response}")
            content_plan = json.loads(response)
            
            # Validate required fields
            required_fields = [
                "video_title", "video_description", "hook", "scenes",
                "conclusion", "music_suggestion",
            ]
            
            for field in required_fields:
                if field not in content_plan:
                    raise ValueError(f"Missing required field: {field}")
            
            return content_plan
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {str(e)}")
            raise e
        except Exception as e:
            self.logger.error(f"Error parsing response: {str(e)}")
            raise e
    
    def _get_error_content_plan(self) -> Dict:
        """Generate fallback content when error occurs."""
        return {
            "video_title": "Error Occurred",
            "video_description": "An error occurred while generating content.",
            "hook": {
                "script": "Sorry, an error occurred.",
                "image_keywords": ["error", "apology"],
                "visual_style": "Simple, minimalistic"
            },
            "scenes": [
                {
                    "title": "Error Occurred",
                    "script": "An error occurred while generating content.",
                    "image_keywords": ["error", "technical_difficulty"],
                    "visual_style": "Simple, minimalistic"
                }
            ],
            "conclusion": {
                "script": "We apologize for the inconvenience.",
                "image_keywords": ["apology", "retry"],
                "visual_style": "Simple, minimalistic"
            },
            "music_suggestion": "Soft, apologetic background music",
        } 