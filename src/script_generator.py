import json
import os
from typing import Dict, Optional
from dataclasses import dataclass
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import SCRIPT_TEMPLATE

@dataclass
class ScriptConfig:
    topic: str
    target_audience: str
    mood: str
    tone: str
    duration: int  # 초 단위

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
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        self.client = OpenAI(api_key=api_key)
    
    def generate_script(self, config: ScriptConfig) -> str:
        """설정에 따라 스크립트를 생성합니다."""
        # 캐시 확인
        script_key = self._generate_script_key(config)
        cached_script = self._get_cached_script(script_key)
        if cached_script:
            return cached_script
        
        try:
            # 프롬프트 생성
            prompt = SCRIPT_TEMPLATE.format(
                topic=config.topic,
                target_audience=config.target_audience,
                mood=config.mood
            )
            
            # LLM을 사용하여 스크립트 생성
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a professional script writer for YouTube Shorts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            script = response.choices[0].message.content
            
            # 효과음 마커 추가
            script = self._add_sound_effects(script)
            
            # 캐시에 저장
            self._cache_script(script_key, script)
            
            return script
        except Exception as e:
            print(f"스크립트 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_script(config)
    
    def _generate_script_key(self, config: ScriptConfig) -> str:
        """스크립트 캐시 키를 생성합니다."""
        return f"{config.topic}_{config.target_audience}_{config.mood}_{config.tone}_{config.duration}"
    
    def _get_cached_script(self, script_key: str) -> Optional[str]:
        """캐시된 스크립트를 가져옵니다."""
        script_data = self._load_script_data()
        return script_data.get(script_key)
    
    def _cache_script(self, script_key: str, script: str):
        """스크립트를 캐시에 저장합니다."""
        script_data = self._load_script_data()
        script_data[script_key] = script
        self._save_script_data(script_data)
    
    def _load_script_data(self) -> Dict:
        """저장된 스크립트 데이터를 로드합니다."""
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def _save_script_data(self, script_data: Dict):
        """스크립트 데이터를 저장합니다."""
        with open(self.storage_path, 'w') as f:
            json.dump(script_data, f, indent=2)
    
    def _add_sound_effects(self, script: str) -> str:
        """스크립트에 효과음 마커를 추가합니다."""
        lines = script.split('\n')
        enhanced_lines = []
        
        for line in lines:
            if line.strip().startswith('[HOOK]'):
                enhanced_lines.append(line)
                enhanced_lines.append('(효과음: whoosh)')
            elif line.strip().startswith('[CONTENT]'):
                enhanced_lines.append(line)
                enhanced_lines.append('(효과음: click)')
            elif line.strip().startswith('[CONCLUSION]'):
                enhanced_lines.append(line)
                enhanced_lines.append('(효과음: ding)')
            else:
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _generate_dummy_script(self, config: ScriptConfig) -> str:
        """오류 발생 시 사용할 더미 스크립트를 생성합니다."""
        return f"""[HOOK]
(효과음: whoosh)
안녕하세요! 오늘은 {config.topic}에 대해 이야기해볼게요.

[CONTENT]
(효과음: click)
첫 번째로, 이것은 매우 중요한 포인트입니다.
두 번째로, 이것도 꼭 기억해주세요.
마지막으로, 이것이 핵심입니다.

[CONCLUSION]
(효과음: ding)
지금까지 설명한 내용이 도움이 되셨나요?""" 