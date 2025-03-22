import json
import os
from typing import Dict, Optional
from dataclasses import dataclass
import openai
from dotenv import load_dotenv

@dataclass
class ScriptConfig:
    content_plan: Dict
    target_audience: str
    tone: str
    duration: float

class ScriptGenerator:
    def __init__(self):
        self.storage_path = "data/scripts.json"
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
    
    def generate_script(self, content_plan: Dict, target_audience: str = "general",
                       tone: str = "informative", duration: float = 60.0) -> str:
        """콘텐츠 계획을 바탕으로 스크립트를 생성합니다."""
        config = ScriptConfig(content_plan, target_audience, tone, duration)
        
        # 캐시 확인
        cache_key = self._create_cache_key(config)
        cached_script = self._get_cached_script(cache_key)
        if cached_script:
            return cached_script
        
        # 새로운 스크립트 생성
        prompt = self._create_script_prompt(config)
        response = self._get_llm_response(prompt)
        
        # 효과음 마커 추가
        script_with_effects = self._add_sound_effects(response)
        
        # 캐시에 저장
        self._cache_script(cache_key, script_with_effects)
        
        return script_with_effects
    
    def _create_script_prompt(self, config: ScriptConfig) -> str:
        """스크립트 생성을 위한 프롬프트를 생성합니다."""
        return f"""
Create a script for a {config.duration}-second YouTube Short video based on this content plan:

Hook:
{config.content_plan['hook']}

Main Points:
{chr(10).join(config.content_plan['main_points'])}

Conclusion:
{config.content_plan['conclusion']}

Target audience: {config.target_audience}
Tone: {config.tone}

Please structure the script with [HOOK], [CONTENT], and [CONCLUSION] sections.
Make it engaging and suitable for short-form video content.
Keep sentences short and impactful.
Use conversational language that resonates with {config.target_audience} audience.
"""
    
    def _get_llm_response(self, prompt: str) -> str:
        """LLM으로부터 응답을 받아옵니다."""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional scriptwriter specializing in short-form video content."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    
    def _add_sound_effects(self, script: str) -> str:
        """스크립트에 효과음 마커를 추가합니다."""
        # Hook 효과음
        script = script.replace("[HOOK]", "[HOOK]\n[SOUND:whoosh]")
        
        # Content 효과음
        lines = script.split("\n")
        modified_lines = []
        for line in lines:
            if line.strip().startswith("[CONTENT]"):
                modified_lines.append(line)
                modified_lines.append("[SOUND:pop]")
            else:
                modified_lines.append(line)
        
        # Conclusion 효과음
        script = "\n".join(modified_lines)
        script = script.replace("[CONCLUSION]", "[SOUND:ding]\n[CONCLUSION]")
        
        return script
    
    def _create_cache_key(self, config: ScriptConfig) -> str:
        """캐시 키를 생성합니다."""
        return f"{hash(str(config.content_plan))}_{config.target_audience}_{config.tone}_{config.duration}"
    
    def _get_cached_script(self, cache_key: str) -> Optional[str]:
        """캐시된 스크립트를 가져옵니다."""
        scripts = self._load_scripts()
        return scripts.get(cache_key)
    
    def _cache_script(self, cache_key: str, script: str):
        """스크립트를 캐시에 저장합니다."""
        scripts = self._load_scripts()
        scripts[cache_key] = script
        self._save_scripts(scripts)
    
    def _load_scripts(self) -> Dict:
        """저장된 스크립트를 로드합니다."""
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def _save_scripts(self, scripts: Dict):
        """스크립트를 저장합니다."""
        with open(self.storage_path, 'w') as f:
            json.dump(scripts, f, indent=2)
    
    def _create_script_template(self, game_name: str, tone: str, target_audience: str) -> str:
        """스크립트 템플릿을 생성합니다."""
        return f"""
[HOOK]
Hey {target_audience}! Ready to dive into {game_name}? Let's explore what makes this game absolutely amazing!

[CONTENT]
1. First up, {game_name} brings unique gameplay mechanics that will keep you hooked!
2. The multiplayer experience is next-level, with {tone} interactions that make every session memorable.
3. And here's something you might not know - the game's community is growing faster than ever!

[CONCLUSION]
So what are you waiting for? Jump into {game_name} now and experience the excitement for yourself! Don't forget to like and subscribe for more gaming content!
""" 