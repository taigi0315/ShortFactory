import json
import os
from typing import Dict
import openai
from dotenv import load_dotenv

class ContentGenerator:
    def __init__(self):
        self.storage_path = "data/content_plans.json"
        self._ensure_storage_exists()
        self._setup_llm()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리와 파일이 존재하는지 확인합니다."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)
    
    def _setup_llm(self):
        """LLM 연결을 설정합니다."""
        # 환경 변수 로드
        load_dotenv()
        
        # OpenAI API 키 확인
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        self.client = openai.OpenAI()
    
    def generate_content(self, topic: str, target_audience: str, mood: str) -> Dict:
        """주어진 주제에 대한 콘텐츠 계획을 생성합니다."""
        # 캐시 확인
        cache_key = f"{topic}_{target_audience}_{mood}"
        cached_plan = self._get_cached_plan(cache_key)
        if cached_plan:
            return cached_plan
        
        # 새로운 콘텐츠 계획 생성
        prompt = self._create_content_prompt(topic, target_audience, mood)
        response = self._get_llm_response(prompt)
        
        # 응답을 구조화된 형식으로 변환
        content_plan = self._parse_llm_response(response)
        
        # 캐시에 저장
        self._cache_plan(cache_key, content_plan)
        
        return content_plan
    
    def _create_content_prompt(self, topic: str, target_audience: str, mood: str) -> str:
        """콘텐츠 생성용 프롬프트를 생성합니다."""
        return f"""
Create a content plan for a YouTube Short video about {topic}.

Target audience: {target_audience}
Mood: {mood}

Please provide a structured plan with the following sections:
1. Hook (attention-grabbing opening)
2. Main points (3-4 key points)
3. Conclusion (call to action)

Make it engaging and suitable for short-form video content.
"""
    
    def _get_llm_response(self, prompt: str) -> str:
        """LLM으로부터 응답을 받아옵니다."""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional content creator specializing in short-form video content."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    def _parse_llm_response(self, response: str) -> Dict:
        """LLM 응답을 구조화된 형식으로 변환합니다."""
        # 간단한 파싱 로직 (실제로는 더 복잡한 파싱이 필요할 수 있음)
        sections = response.split("\n\n")
        content_plan = {
            "hook": sections[0] if len(sections) > 0 else "",
            "main_points": sections[1].split("\n") if len(sections) > 1 else [],
            "conclusion": sections[2] if len(sections) > 2 else ""
        }
        return content_plan
    
    def _get_cached_plan(self, cache_key: str) -> Dict:
        """캐시된 콘텐츠 계획을 가져옵니다."""
        plans = self._load_plans()
        return plans.get(cache_key)
    
    def _cache_plan(self, cache_key: str, plan: Dict):
        """콘텐츠 계획을 캐시에 저장합니다."""
        plans = self._load_plans()
        plans[cache_key] = plan
        self._save_plans(plans)
    
    def _load_plans(self) -> Dict:
        """저장된 콘텐츠 계획을 로드합니다."""
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def _save_plans(self, plans: Dict):
        """콘텐츠 계획을 저장합니다."""
        with open(self.storage_path, 'w') as f:
            json.dump(plans, f, indent=2) 