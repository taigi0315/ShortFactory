import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import openai
from dotenv import load_dotenv
from .prompts import SYSTEM_PROMPTS, get_visual_selection_prompt
from .ai_image_generator import AIImageGenerator
from .utils.logger import Logger

class VisualSource(Enum):
    WEB_SEARCH = "web_search"
    AI_IMAGE = "ai_image"
    AI_VIDEO = "ai_video"

@dataclass
class VisualAsset:
    type: str  # "image" or "video"
    content: str  # URL or prompt
    timing: float
    duration: float
    source_type: VisualSource
    metadata: Optional[Dict] = None

class VisualSelector:
    def __init__(self):
        self.visual_dir = "data/visuals"
        os.makedirs(self.visual_dir, exist_ok=True)
        self._setup_llm()
        self.ai_generator = AIImageGenerator()
        self.logger = Logger()
    
    def _setup_llm(self):
        """LLM 연결을 설정합니다."""
        # Load environment variables from .env file in project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(project_root, '.env'))
        
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        self.client = openai.OpenAI()
    
    def select_visuals(self, script: Dict, target_audience: str, mood: str) -> List[Dict]:
        """스크립트에 맞는 시각적 에셋을 선택합니다."""
        self.logger.section("시각적 에셋 생성 시작")
        self.logger.info(f"대상: {target_audience}")
        self.logger.info(f"분위기: {mood}")
        
        # 새로운 시각적 에셋 생성
        visual_assets = []
        
        # 시각적 선택 프롬프트 생성
        prompt = get_visual_selection_prompt(
            script=json.dumps(script, ensure_ascii=False),
            target_audience=target_audience,
            mood=mood
        )
        
        # 프롬프트 출력
        self.logger.subsection("프롬프트")
        self.logger.info(f"시스템 프롬프트: {SYSTEM_PROMPTS['visual_director']}")
        self.logger.info(f"사용자 프롬프트: {prompt}")
        
        # LLM을 사용하여 시각적 프롬프트 생성
        self.logger.process("GPT-4에게 시각적 계획 생성 요청 중...")
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS["visual_director"]},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 응답 출력
        self.logger.subsection("생성된 시각적 계획")
        self.logger.info(response.choices[0].message.content)
        
        self.logger.process("시각적 계획 파싱 중...")
        visual_plan = self._parse_visual_plan(response.choices[0].message.content)
        
        # 각 섹션에 대한 시각적 에셋 생성
        self.logger.subsection("시각적 에셋 생성")
        for i, section in enumerate(visual_plan["sections"], 1):
            self.logger.process(f"섹션 {i} 시각적 에셋 생성 중...")
            self.logger.info(f"타입: {section['type']}")
            self.logger.info(f"설명: {section['description']}")
            self.logger.info(f"효과: {section.get('effect', 'none')}")
            
            visual = self._create_visual_for_section(
                section["type"],
                section["description"],
                section.get("effect", "none")
            )
            visual_assets.append(visual)
            self.logger.success(f"섹션 {i} 시각적 에셋 생성 완료: {visual['content']}")
        
        self.logger.success("모든 시각적 에셋 생성 완료")
        return visual_assets
    
    def _parse_visual_plan(self, response: str) -> Dict:
        """LLM 응답을 구조화된 형식으로 변환합니다."""
        sections = response.split("\n\n")
        visual_plan = {
            "sections": []
        }
        
        current_section = None
        for section in sections:
            if section.startswith("Scene:"):
                if current_section:
                    visual_plan["sections"].append(current_section)
                current_section = {
                    "type": "scene",
                    "description": section.replace("Scene:", "").strip(),
                    "effect": "none"
                }
            elif section.startswith("Effect:") and current_section:
                current_section["effect"] = section.replace("Effect:", "").strip()
        
        if current_section:
            visual_plan["sections"].append(current_section)
        
        return visual_plan
    
    def _create_visual_for_section(self, section_type: str, description: str, effect: str) -> Dict:
        """섹션에 맞는 시각적 에셋을 생성합니다."""
        try:
            # 시각적 소스 타입 결정
            source_type = self._determine_visual_type(section_type)
            self.logger.info(f"선택된 소스 타입: {source_type.value}")
            
            # 시각적 에셋 생성
            visual = self._get_visual_from_source(
                source_type,
                description,
                effect
            )
            
            return visual
        except Exception as e:
            self.logger.error(f"시각적 에셋 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_visual(section_type)
    
    def _determine_visual_type(self, section_type: str) -> VisualSource:
        """섹션 타입에 따라 적절한 시각적 소스를 결정합니다."""
        if section_type == "scene":
            return VisualSource.AI_IMAGE
        else:
            return VisualSource.WEB_SEARCH
    
    def _get_visual_from_source(self, source_type: VisualSource, prompt: str, effect: str) -> Dict:
        """선택된 소스에서 시각적 에셋을 가져옵니다."""
        try:
            if source_type == VisualSource.AI_IMAGE:
                # AI 이미지 생성
                self.logger.process(f"AI 이미지 생성 중... (프롬프트: {prompt})")
                image_path = self.ai_generator.generate_image(
                    prompt=prompt,
                    output_path=f"{self.visual_dir}/image_{hash(prompt)}.png"
                )
                
                return {
                    "type": "image",
                    "content": image_path,
                    "timing": 0.0,
                    "duration": 2.0,
                    "source_type": source_type.value,
                    "metadata": {
                        "generation_type": "ai_image",
                        "prompt": prompt,
                        "effect": effect
                    }
                }
            else:  # WEB_SEARCH
                # 웹 검색 이미지는 아직 구현되지 않음
                self.logger.warning("웹 검색 이미지는 아직 구현되지 않아 더미 이미지를 사용합니다.")
                return {
                    "type": "image",
                    "content": "data/images/dummy.png",
                    "timing": 0.0,
                    "duration": 2.0,
                    "source_type": source_type.value,
                    "metadata": {
                        "generation_type": "web_search",
                        "search_query": prompt
                    }
                }
        except Exception as e:
            self.logger.error(f"시각적 에셋 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_visual("scene")
    
    def _generate_dummy_visual(self, section_type: str) -> Dict:
        """오류 발생 시 사용할 더미 시각적 에셋을 생성합니다."""
        try:
            # 기본 프롬프트 생성
            prompt = f"Create a simple {section_type} visual for a YouTube Short"
            self.logger.process(f"더미 시각적 에셋 생성 중... (프롬프트: {prompt})")
            
            # 이미지 생성
            image_path = self.ai_generator.generate_image(
                prompt=prompt,
                output_path=f"{self.visual_dir}/fallback_{section_type}_{hash(prompt)}.png"
            )
            
            return {
                "type": "image",
                "content": image_path,
                "timing": 0.0,
                "duration": 2.0,
                "source_type": "ai_image",
                "metadata": {
                    "generation_type": "fallback_image",
                    "prompt": prompt
                }
            }
        except Exception as e:
            self.logger.error(f"대체 이미지 생성 중 오류 발생: {str(e)}")
            # 최후의 수단으로 검은 화면 이미지 생성
            black_screen_path = self._create_black_screen()
            return {
                "type": "image",
                "content": black_screen_path,
                "timing": 0.0,
                "duration": 2.0,
                "source_type": "fallback",
                "metadata": {
                    "generation_type": "black_screen"
                }
            }
    
    def _create_black_screen(self) -> str:
        """검은 화면 이미지를 생성합니다."""
        try:
            import numpy as np
            from PIL import Image
            
            self.logger.process("검은 화면 이미지 생성 중...")
            
            # 1920x1080 크기의 검은 화면 이미지 생성
            black_screen = np.zeros((1080, 1920, 3), dtype=np.uint8)
            image = Image.fromarray(black_screen)
            
            # 저장 경로 생성
            output_path = "data/images/black_screen.png"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 이미지 저장
            image.save(output_path)
            self.logger.success(f"검은 화면 이미지 생성 완료: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"검은 화면 이미지 생성 중 오류 발생: {str(e)}")
            return "data/images/black_screen.png" 