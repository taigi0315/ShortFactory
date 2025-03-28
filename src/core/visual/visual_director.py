"""
시각적 에셋 생성을 담당하는 VisualDirector 클래스

이 클래스는 LLM을 사용하여 콘텐츠에 맞는 시각적 에셋을 생성합니다.
주요 기능:
- 콘텐츠 계획에 따른 이미지 생성
- 대상 청중과 분위기에 맞는 시각적 스타일 결정
- 생성된 이미지의 품질 관리
"""

from typing import Dict, List, Any
from ...utils.logger import Logger
from ..content.prompts import get_visual_director_prompt
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
import json
import uuid
from config.styles import image_styles

class VisualDirector:
    def __init__(self, task_id: str):
        self.logger = Logger()
        self.API_KEY_NAME = "GOOGLE_API_KEY"
        self._setup_llm()
        self.task_id = task_id
        self.output_dir = os.path.join("data", task_id)
        self.output_dir_image = os.path.join(self.output_dir, "images")
        self.output_dir_prompt = os.path.join(self.output_dir, "prompts")
        os.makedirs(self.output_dir_image, exist_ok=True)
        os.makedirs(self.output_dir_prompt, exist_ok=True)
    
    def _setup_llm(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(project_root, '.env'))

        if not os.getenv(self.API_KEY_NAME):
            raise ValueError(
                "Google API key not found. Please set the GOOGLE_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
    
        self.client = genai.Client(api_key=os.getenv(self.API_KEY_NAME))
    
    def create_visuals(self, content_plan: Dict[str, Any], creator: str) -> List[Dict[str, Any]]:
        """Generate visual assets for the content plan."""
        try:
            visuals = []
            
            # Create hook image
            self.logger.subsection("Hook scene creation")
            # validate hook visual
            self.logger.subsection("Hook scene validation")
            if not self._validate_visual_asset(content_plan["hook"]):
                raise ValueError("Hook visual asset is invalid")
            hook_visual = self._create_scene_visual(
                content_plan["hook"],
                "hook",
                creator
            )
            visuals.append(hook_visual)
            
            # Create scene images
            self.logger.subsection("Scene creation")
            for i, point in enumerate(content_plan["scenes"], 1):
                self.logger.info(f"Point {i} creation in progress...")
                # validate scene visual
                self.logger.subsection(f"{i} Scene scene validation")
                if not self._validate_visual_asset(point):
                    raise ValueError("Scene visual asset is invalid")
                point_visual = self._create_scene_visual(
                    point,
                    f"scene_{i}",
                    creator
                )
                visuals.append(point_visual)
            
            # Create conclusion image
            self.logger.subsection("Conclusion scene creation")
            # validate conclusion visual
            self.logger.subsection("Conclusion scene validation")
            if not self._validate_visual_asset(content_plan["conclusion"]):
                raise ValueError("Conclusion visual asset is invalid")
            conclusion_visual = self._create_scene_visual(
                content_plan["conclusion"],
                "conclusion",
                creator
            )
            visuals.append(conclusion_visual)
            
            self.logger.success(f"Total {len(visuals)} visual assets created")
            return visuals
            
        except Exception as e:
            self.logger.error(f"Error generating visual assets: {str(e)}")
            raise e
    
    def _create_scene_visual(self, scene: Dict[str, Any], scene_name: str, creator: str) -> Dict[str, Any]:
        """
        개별 장면에 대한 시각적 에셋을 생성합니다.

        Args:
            scene (Dict[str, Any]): 장면 정보
            scene_name (str): 장면 이름 (파일명에 사용)
            creator (str): creator 이름

        Returns:
            Dict[str, Any]: 생성된 시각적 에셋 정보
        """
        try:
            # Create prompt with style details
            prompt = get_visual_director_prompt(
                script=scene["script"],
                scene_description=scene["scene_description"],
                image_keywords=", ".join(scene["image_keywords"]),
                image_style_name=scene["image_style_name"],  # Use the scene's image_style
                image_to_video=scene.get("image_to_video", ""),
                creator=creator
            )
            
            # Save prompt to file
            with open(os.path.join(self.output_dir_prompt, f"{scene_name}_image_prompt.txt"), "w") as f:
                f.write(prompt)
                
            # Call Gemini API
            self.logger.info("Calling Gemini API...")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=types.Content(
                    parts=[types.Part(text=prompt)]
                ),
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # Process response
            image_path = os.path.join(self.output_dir_image, f"{scene_name}.png")
            
            if not response or not response.candidates:
                self.logger.error("No response received from Gemini API")
                raise Exception("Failed to generate content: No response received")
                
            if not response.candidates[0].content:
                self.logger.error("Empty content in Gemini API response")
                raise Exception("Failed to generate content: Empty response content")
                
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    self.logger.info(f"Generated text: {part.text}")
                elif part.inline_data is not None:
                    image = Image.open(BytesIO((part.inline_data.data)))
                    image.save(image_path)
                    self.logger.info(f"Image saved: {image_path}")
            
            return {
                "scene_title": scene.get("title", ""),
                "image_path": image_path,
                "animation_type": scene.get("image_to_video", ""),
                "style": scene["image_style_name"]  # Use the scene's image_style
            }
            
        except Exception as e:
            self.logger.error(f"Error create scene visual assets: {str(e)}")
            raise

    def _validate_visual_asset(self, visual_asset: Dict[str, Any]) -> bool:
        """
        시각적 에셋의 유효성을 검사합니다.

        Args:
            visual (Dict[str, Any]): 시각적 에셋 정보
        """
        try:
            required_fields = ["script", "image_keywords", "scene_description", "image_to_video"]
            for field in required_fields:
                if field not in visual_asset:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # image_style_name이 없으면 기본 스타일 설정
            if "image_style_name" not in visual_asset:
                visual_asset["image_style_name"] = "modern"  # 기본 스타일
                self.logger.info("Using default image style: modern")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error validating visual assets: {str(e)}")
            return False