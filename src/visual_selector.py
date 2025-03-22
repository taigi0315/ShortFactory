import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import VISUAL_PROMPT_TEMPLATE

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
        self.storage_path = "data/visuals.json"
        self.visual_dir = "data/visuals"
        self._ensure_storage_exists()
        self._setup_apis()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리와 파일이 존재하는지 확인합니다."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        os.makedirs(self.visual_dir, exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)
    
    def _setup_apis(self):
        """API 연결을 설정합니다."""
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        self.client = OpenAI(api_key=api_key)
    
    def select_visuals(self, script: str, topic: str, target_audience: str, mood: str) -> List[Dict]:
        """스크립트에 맞는 시각적 에셋을 선택합니다."""
        # 캐시 확인
        script_key = str(hash(script))
        cached_visuals = self._get_cached_visuals(script_key)
        if cached_visuals:
            return cached_visuals
        
        # 새로운 시각적 에셋 생성
        visual_assets = []
        
        # 스크립트의 각 섹션에 대해 시각적 에셋 생성
        sections = self._parse_script_sections(script)
        for section_type, section_content in sections.items():
            visual = self._create_visual_for_section(
                section_type,
                section_content,
                topic,
                target_audience,
                mood
            )
            visual_assets.append(visual)
        
        # 캐시에 저장
        self._cache_visuals(script_key, visual_assets)
        
        return visual_assets
    
    def _parse_script_sections(self, script: str) -> Dict[str, str]:
        """스크립트를 섹션별로 파싱합니다."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in script.split("\n"):
            if line.strip() == "[HOOK]":
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "hook"
                current_content = []
            elif line.strip() == "[CONTENT]":
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "content"
                current_content = []
            elif line.strip() == "[CONCLUSION]":
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content)
                current_section = "conclusion"
                current_content = []
            elif current_section and line.strip():
                current_content.append(line.strip())
        
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content)
        
        return sections
    
    def _create_visual_for_section(self, section_type: str, content: str,
                                 topic: str, target_audience: str, mood: str) -> Dict:
        """섹션에 맞는 시각적 에셋을 생성합니다."""
        # 시각적 소스 타입 결정
        source_type = self._determine_visual_type(section_type)
        
        # 프롬프트 생성
        prompt = VISUAL_PROMPT_TEMPLATE.format(
            topic=topic,
            target_audience=target_audience,
            mood=mood,
            section=section_type
        )
        
        try:
            # LLM을 사용하여 시각적 프롬프트 생성
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a professional visual content creator for YouTube Shorts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            visual_prompt = response.choices[0].message.content
            
            # 시각적 에셋 생성
            visual = self._get_visual_from_source(
                source_type,
                visual_prompt,
                section_type
            )
            
            return visual
        except Exception as e:
            print(f"시각적 에셋 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_visual(section_type)
    
    def _determine_visual_type(self, section_type: str) -> VisualSource:
        """섹션 타입에 따라 적절한 시각적 소스를 결정합니다."""
        if section_type == "hook":
            return VisualSource.AI_VIDEO  # 훅은 동적인 비디오가 효과적
        elif section_type == "content":
            return VisualSource.AI_IMAGE  # 콘텐츠는 정적인 이미지가 적합
        else:  # conclusion
            return VisualSource.WEB_SEARCH  # 결론은 웹 이미지로 충분
    
    def _get_visual_from_source(self, source_type: VisualSource,
                              prompt: str, section_type: str) -> Dict:
        """선택된 소스에서 시각적 에셋을 가져옵니다."""
        if source_type == VisualSource.AI_VIDEO:
            return {
                "type": "video",
                "content": prompt,
                "timing": 0.0 if section_type == "hook" else 5.0,
                "duration": 3.0,
                "source_type": source_type.value,
                "metadata": {
                    "generation_type": "ai_video",
                    "prompt": prompt
                }
            }
        elif source_type == VisualSource.AI_IMAGE:
            return {
                "type": "image",
                "content": prompt,
                "timing": 5.0 if section_type == "content" else 8.0,
                "duration": 2.0,
                "source_type": source_type.value,
                "metadata": {
                    "generation_type": "ai_image",
                    "prompt": prompt
                }
            }
        else:  # WEB_SEARCH
            return {
                "type": "image",
                "content": prompt,
                "timing": 8.0 if section_type == "conclusion" else 10.0,
                "duration": 2.0,
                "source_type": source_type.value,
                "metadata": {
                    "generation_type": "web_search",
                    "search_query": prompt
                }
            }
    
    def _generate_dummy_visual(self, section_type: str) -> Dict:
        """오류 발생 시 사용할 더미 시각적 에셋을 생성합니다."""
        return {
            "type": "image",
            "content": f"Dummy visual for {section_type}",
            "timing": 0.0,
            "duration": 2.0,
            "source_type": VisualSource.WEB_SEARCH.value,
            "metadata": {
                "error": "Failed to generate visual"
            }
        }
    
    def _get_cached_visuals(self, script_key: str) -> Optional[List[Dict]]:
        """캐시된 시각적 에셋을 가져옵니다."""
        visual_data = self._load_visual_data()
        return visual_data.get(script_key)
    
    def _cache_visuals(self, script_key: str, visual_assets: List[Dict]):
        """시각적 에셋을 캐시에 저장합니다."""
        visual_data = self._load_visual_data()
        visual_data[script_key] = visual_assets
        self._save_visual_data(visual_data)
    
    def _load_visual_data(self) -> Dict:
        """저장된 시각적 데이터를 로드합니다."""
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def _save_visual_data(self, visual_data: Dict):
        """시각적 데이터를 저장합니다."""
        with open(self.storage_path, 'w') as f:
            json.dump(visual_data, f, indent=2) 