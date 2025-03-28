"""
이미지 생성을 담당하는 ImageGenerator 클래스

이 클래스는 LLM을 사용하여 콘텐츠에 맞는 이미지를 생성합니다.
주요 기능:
- 프롬프트 기반 이미지 생성
- 스타일 적용
- 이미지 품질 관리
"""

from typing import Dict, Any
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
from ..content.prompts import get_visual_director_prompt
from ...utils.logger import Logger

class ImageGenerator:
    def __init__(self):
        self.logger = Logger()
        self.API_KEY_NAME = "GOOGLE_API_KEY"
        self._setup_llm()
    
    def _setup_llm(self):
        """LLM 설정을 초기화합니다."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        load_dotenv(os.path.join(project_root, '.env'))

        if not os.getenv(self.API_KEY_NAME):
            raise ValueError(
                "Google API key not found. Please set the GOOGLE_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
    
        self.client = genai.Client(api_key=os.getenv(self.API_KEY_NAME))
    
    def generate_image(self, scene_description: str, style: str = "default", creator: str = None, task_id: str = None) -> bytes:
        """
        주어진 설명과 스타일에 따라 이미지를 생성합니다.

        Args:
            scene_description (str): 장면 설명
            style (str): 이미지 스타일
            creator (str): 크리에이터 ID
            task_id (str): 작업 ID

        Returns:
            bytes: 생성된 이미지 데이터
        """
        try:
            # 프롬프트 생성
            prompt = get_visual_director_prompt(
                script="",
                scene_description=scene_description,
                image_keywords="",
                image_style_name=style,
                image_to_video="",
                creator=creator
            )
            
            # 프롬프트 저장
            if creator and task_id:
                prompts_dir = os.path.join("data", creator, task_id, "prompts")
                os.makedirs(prompts_dir, exist_ok=True)
                prompt_path = os.path.join(prompts_dir, f"image_prompt_{style}.txt")
                with open(prompt_path, "w", encoding="utf-8") as f:
                    f.write(prompt)
            
            # Gemini API 호출
            self.logger.info("Calling Gemini API for image generation...")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=types.Content(
                    parts=[types.Part(text=prompt)]
                ),
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            if not response or not response.candidates:
                self.logger.error("No response received from Gemini API")
                raise Exception("Failed to generate content: No response received")
                
            if not response.candidates[0].content:
                self.logger.error("Empty content in Gemini API response")
                raise Exception("Failed to generate content: Empty response content")
                
            # 이미지 데이터 추출
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    return part.inline_data.data
            
            raise Exception("No image data found in response")
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            raise 