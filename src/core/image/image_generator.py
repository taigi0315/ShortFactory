"""
이미지 생성을 담당하는 ImageGenerator 클래스

이 클래스는 LLM을 사용하여 콘텐츠에 맞는 이미지를 생성합니다.
지원하는 모델:
- Gemini: Google의 Gemini 모델
- OpenAI: OpenAI의 DALL-E 모델
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
import openai
import time

class ImageGenerator:
    def __init__(self, model: str = "gemini"):
        """
        Args:
            model (str): 사용할 모델 ("gemini" 또는 "gpt-4o")
        """
        self.logger = Logger()
        self.model = model.lower()
        
        if self.model not in ["gemini", "gpt-4o"]:
            raise ValueError("Unsupported model. Use 'gemini' or 'gpt-4o'")
        
        if self.model == "gemini":
            self.GOOGLE_API_KEY = "GOOGLE_API_KEY"
            self._setup_gemini()
        else:
            self.OPENAI_API_KEY = "OPENAI_API_KEY"
            self._setup_openai()
    
    def _setup_gemini(self):
        """Gemini API 설정을 초기화합니다."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        load_dotenv(os.path.join(project_root, '.env'))

        if not os.getenv(self.GOOGLE_API_KEY):
            raise ValueError(
                "Google API key not found. Please set the GOOGLE_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
    
        self.gemini_client = genai.Client(api_key=os.getenv(self.GOOGLE_API_KEY))
    
    def _setup_openai(self):
        """OpenAI API 설정을 초기화합니다."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        load_dotenv(os.path.join(project_root, '.env'))

        if not os.getenv(self.OPENAI_API_KEY):
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        openai.api_key = os.getenv(self.OPENAI_API_KEY)
    
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
        time.sleep(5)
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
            
            # 모델에 따라 이미지 생성
            if self.model == "gemini":
                return self._generate_with_gemini(prompt)
            else:
                return self._generate_with_openai(prompt)
            
        except Exception as e:
            self.logger.error(f"Error generating image: {str(e)}")
            raise
    
    def _generate_with_gemini(self, prompt: str) -> bytes:
        """Gemini 모델을 사용하여 이미지를 생성합니다."""
        self.logger.info("Calling Gemini API for image generation...")
        response = self.gemini_client.models.generate_content(
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
    
    def _generate_with_openai(self, prompt: str) -> bytes:
        """OpenAI DALL-E 모델을 사용하여 이미지를 생성합니다."""
        self.logger.info("Calling OpenAI API for image generation...")
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json"
        )
        
        if not response or not response.data:
            raise Exception("Failed to generate image with OpenAI")
        
        import base64
        image_data = base64.b64decode(response.data[0].b64_json)
        return image_data 