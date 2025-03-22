import json
import os
from typing import Dict, List, Optional
from enum import Enum
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from .prompts import AUDIO_PROMPT_TEMPLATE
import random

class AudioType(Enum):
    BACKGROUND_MUSIC = "background_music"
    SOUND_EFFECT = "sound_effect"
    NARRATION = "narration"

class AudioGenerator:
    def __init__(self):
        self._ensure_storage_exists()
        self._setup_api()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리와 파일이 존재하는지 확인합니다."""
        self.audio_dir = "data/audio"
        self.storage_file = "data/audio_assets.json"
        os.makedirs(self.audio_dir, exist_ok=True)
        
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump({}, f)
    
    def _setup_api(self):
        """ElevenLabs API 설정을 초기화합니다."""
        load_dotenv()
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError(
                "ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        self.client = ElevenLabs(api_key=api_key)
    
    def generate_audio(self, script: Dict, topic: str, target_audience: str, mood: str) -> Dict:
        """스크립트를 기반으로 오디오 에셋을 생성합니다."""
        try:
            # 1. 나레이션 생성
            narration = self._generate_narration(script["narration"])
            
            # 2. 효과음 생성
            sound_effects = self._generate_sound_effects(script["sound_effects"])
            
            return {
                "narration": narration,
                "sound_effects": sound_effects
            }
        except Exception as e:
            print(f"오디오 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_audio()
    
    def _generate_narration(self, text: str) -> str:
        """텍스트를 음성으로 변환합니다."""
        try:
            # 음성 선택 (기본 음성 사용)
            available_voices = self.client.voices.get_all()
            voice = available_voices[0]
            
            # 오디오 생성
            audio = self.client.generate(
                text=text,
                voice=voice,
                model="eleven_multilingual_v2"
            )
            
            # 파일로 저장
            output_path = os.path.join(self.audio_dir, "narration.mp3")
            with open(output_path, "wb") as f:
                f.write(audio)
            
            return output_path
            
        except Exception as e:
            print(f"나레이션 생성 중 오류 발생: {str(e)}")
            return "data/audio/dummy_narration.mp3"
    
    def _generate_sound_effects(self, effects: List[str]) -> List[str]:
        """효과음 파일 경로 목록을 생성합니다."""
        try:
            # 임시 더미 효과음 파일 생성
            output_paths = []
            for effect in effects:
                output_path = f"data/audio/dummy_effect_{hash(effect)}.mp3"
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                output_paths.append(output_path)
            return output_paths
        except Exception as e:
            print(f"효과음 생성 중 오류 발생: {str(e)}")
            return ["data/audio/dummy_effect.mp3"]
    
    def _generate_dummy_audio(self) -> Dict:
        """오류 발생 시 사용할 더미 오디오 에셋을 생성합니다."""
        return {
            "narration": "data/audio/dummy_narration.mp3",
            "sound_effects": ["data/audio/dummy_effect.mp3"]
        }
    
    def _get_cached_audio(self, script_key: str) -> Optional[List[Dict]]:
        """캐시된 오디오 에셋을 가져옵니다."""
        audio_data = self._load_audio_data()
        return audio_data.get(script_key)
    
    def _cache_audio(self, script_key: str, audio_assets: List[Dict]):
        """오디오 에셋을 캐시에 저장합니다."""
        audio_data = self._load_audio_data()
        audio_data[script_key] = audio_assets
        self._save_audio_data(audio_data)
    
    def _load_audio_data(self) -> Dict:
        """저장된 오디오 데이터를 로드합니다."""
        with open(self.storage_file, 'r') as f:
            return json.load(f)
    
    def _save_audio_data(self, audio_data: Dict):
        """오디오 데이터를 저장합니다."""
        with open(self.storage_file, 'w') as f:
            json.dump(audio_data, f, indent=2) 