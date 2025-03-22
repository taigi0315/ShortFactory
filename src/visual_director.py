"""
시각적 에셋 생성을 담당하는 VisualDirector 클래스

이 클래스는 LLM을 사용하여 콘텐츠에 맞는 시각적 에셋을 생성합니다.
주요 기능:
- 콘텐츠 계획에 따른 이미지 생성
- 대상 청중과 분위기에 맞는 시각적 스타일 결정
- 생성된 이미지의 품질 관리
"""

from typing import Dict, List, Any
from src.utils.logger import Logger
from src.prompts import SYSTEM_PROMPTS, get_visual_director_prompt
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv
import json
import uuid

class VisualDirector:
    def __init__(self, task_id: str):
        self.logger = Logger()
        self.API_KEY_NAME = "GOOGLE_API_KEY"
        self._setup_llm()
        self.task_id = task_id
        self.output_dir_image = os.path.join("data", self.task_id, "images")
        self.output_dir_prompt = os.path.join("data", self.task_id, "prompts")
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
    
    def create_visuals(self, content_plan: Dict[str, Any], target_audience: str, mood: str) -> List[Dict[str, Any]]:
        """
        콘텐츠 계획을 바탕으로 시각적 에셋을 생성합니다.

        Args:
            content_plan (Dict[str, Any]): 콘텐츠 계획 정보
            target_audience (str): 대상 청중
            mood (str): 콘텐츠의 분위기

        Returns:
            List[Dict[str, Any]]: 생성된 시각적 에셋 목록
        """
        self.logger.section("시각적 에셋 생성 시작")
        self.logger.info(f"작업 ID: {self.task_id}")
        self.logger.info("콘텐츠 계획:")
        self.logger.info(json.dumps(content_plan, ensure_ascii=False, indent=2))
        
        try:
            # 각 장면별로 이미지 생성
            visuals = []
            
            # Hook 장면 생성
            self.logger.subsection("Hook 장면 생성")
            hook_visual = self._create_scene_visual(
                content_plan["hook"],
                target_audience,
                mood,
                content_plan["overall_style_guide"],
                "hook"
            )
            visuals.append(hook_visual)
            
            # Main points 장면들 생성
            self.logger.subsection("Main Points 장면 생성")
            for i, point in enumerate(content_plan["main_points"], 1):
                self.logger.info(f"Point {i} 생성 중...")
                point_visual = self._create_scene_visual(
                    point,
                    target_audience,
                    mood,
                    content_plan["overall_style_guide"],
                    f"scene_{i}"
                )
                visuals.append(point_visual)
            
            # Conclusion 장면 생성
            self.logger.subsection("Conclusion 장면 생성")
            conclusion_visual = self._create_scene_visual(
                content_plan["conclusion"],
                target_audience,
                mood,
                content_plan["overall_style_guide"],
                "conclusion"
            )
            visuals.append(conclusion_visual)
            
            self.logger.success(f"총 {len(visuals)}개의 시각적 에셋 생성 완료")
            return visuals
            
        except Exception as e:
            self.logger.error(f"시각적 에셋 생성 중 오류 발생: {str(e)}")
            raise
    
    def _create_scene_visual(self, scene: Dict[str, Any], target_audience: str, mood: str, style_guide: Dict[str, Any], scene_name: str) -> Dict[str, Any]:
        """
        개별 장면에 대한 시각적 에셋을 생성합니다.

        Args:
            scene (Dict[str, Any]): 장면 정보
            target_audience (str): 대상 청중
            mood (str): 콘텐츠의 분위기
            style_guide (Dict[str, Any]): 전체 스타일 가이드
            scene_name (str): 장면 이름 (파일명에 사용)

        Returns:
            Dict[str, Any]: 생성된 시각적 에셋 정보
        """
        try:
            # 프롬프트 생성
            prompt = get_visual_director_prompt(
                script=scene["script"],
                target_audience=target_audience,
                mood=mood,
                visual_style=style_guide["art_style"],
                image_keywords=", ".join(scene["image_keywords"]),
                color_palette=", ".join(style_guide["color_palette"]),
                image_to_video=scene["image_to_video"]
            )
            # Save prompt to file
            with open(os.path.join(self.output_dir_prompt, f"{scene_name}_image_prompt.txt"), "w") as f:
                f.write(prompt)
            # Gemini API 호출
            self.logger.info("Gemini API 호출 중...")
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['Text', 'Image']
                )
            )
            
            # 응답 처리
            image_path = os.path.join(self.output_dir_image, f"{scene_name}.png")
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    self.logger.info(f"생성된 텍스트: {part.text}")
                elif part.inline_data is not None:
                    image = Image.open(BytesIO((part.inline_data.data)))
                    image.save(image_path)
                    self.logger.info(f"이미지 저장 완료: {image_path}")
            
            return {
                "scene_title": scene.get("title", ""),
                "duration_seconds": scene["duration_seconds"],
                "image_path": image_path,
                "animation_type": scene["image_to_video"]
            }
            
        except Exception as e:
            self.logger.error(f"장면 시각적 에셋 생성 중 오류 발생: {str(e)}")
            raise 