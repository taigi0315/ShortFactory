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
from ..image.image_generator import ImageGenerator

class VisualDirector:
    def __init__(self, task_id: str, creator: str):
        self.task_id = task_id
        self.creator = creator
        self.base_dir = os.path.join("data", creator, task_id)
        self.images_dir = os.path.join(self.base_dir, "images")
        self.prompts_dir = os.path.join(self.base_dir, "prompts")
        
        # 디렉토리 생성
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.prompts_dir, exist_ok=True)
        
        self.logger = Logger()
        self.image_generator = ImageGenerator()
    
    def create_visuals(self, content_plan: Dict[str, Any], creator: str) -> Dict[str, Any]:
        """콘텐츠 플랜에 따라 시각 자료를 생성합니다."""
        try:
            # Hook 이미지 생성
            if "hook" in content_plan:
                hook_image = self._create_scene_image(content_plan["hook"], "hook")
                content_plan["hook"]["image_path"] = hook_image
            
            # 각 씬별 이미지 생성
            for i, scene in enumerate(content_plan["scenes"], 1):
                scene["scene_number"] = i  # 씬 번호 설정
                scene_image = self._create_scene_image(scene, f"scene_{i}")
                scene["image_path"] = scene_image
            
            # Conclusion 이미지 생성
            if "conclusion" in content_plan:
                conclusion_image = self._create_scene_image(content_plan["conclusion"], "conclusion")
                content_plan["conclusion"]["image_path"] = conclusion_image
            
            return content_plan
            
        except Exception as e:
            self.logger.error(f"Error creating visuals: {str(e)}")
            raise
    
    def _create_scene_image(self, scene: Dict[str, Any], scene_id: str) -> str:
        """개별 씬의 이미지를 생성합니다."""
        try:
            self.logger.info(f"Creating image for scene: {scene_id}")
            
            # 이미지 생성
            image_data = self.image_generator.generate_image(
                scene.get("scene_description", ""),
                style=scene.get("image_style_name", "default"),
                creator=self.creator,
                task_id=self.task_id
            )
            
            # 이미지 저장
            output_path = os.path.join(self.images_dir, f"{scene_id}.png")
            with open(output_path, "wb") as f:
                f.write(image_data)
            
            self.logger.success(f"Image saved successfully: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating scene image: {str(e)}")
            raise

    def _setup_llm(self):
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(project_root, '.env'))

        if not os.getenv(self.API_KEY_NAME):
            raise ValueError(
                "Google API key not found. Please set the GOOGLE_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
    
        self.client = genai.Client(api_key=os.getenv(self.API_KEY_NAME))
    
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