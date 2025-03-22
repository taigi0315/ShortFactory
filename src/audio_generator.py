import json
import os
from typing import Dict, List, Optional
from enum import Enum
from elevenlabs import generate, Voice, VoiceSettings, voices
from dotenv import load_dotenv
from .prompts import AUDIO_PROMPT_TEMPLATE

class AudioType(Enum):
    BACKGROUND_MUSIC = "background_music"
    SOUND_EFFECT = "sound_effect"
    NARRATION = "narration"

class AudioGenerator:
    def __init__(self):
        self.storage_path = "data/audio.json"
        self.audio_dir = "data/audio"
        self._ensure_storage_exists()
        self._setup_apis()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리와 파일이 존재하는지 확인합니다."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump({}, f)
    
    def _setup_apis(self):
        """API 연결을 설정합니다."""
        load_dotenv()
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            raise ValueError(
                "ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        # ElevenLabs API 키 설정
        os.environ["ELEVEN_API_KEY"] = elevenlabs_api_key
        
        # API 키 유효성 검증
        try:
            available_voices = voices()
            print(f"ElevenLabs API 연결 성공: {len(available_voices)}개의 음성 사용 가능")
        except Exception as e:
            raise ValueError(f"ElevenLabs API key validation failed: {str(e)}")
    
    def generate_audio(self, script: str, topic: str, target_audience: str, mood: str) -> List[Dict]:
        """스크립트에 맞는 오디오 에셋을 생성합니다."""
        # 캐시 확인
        script_key = str(hash(script))
        cached_audio = self._get_cached_audio(script_key)
        if cached_audio:
            return cached_audio
        
        try:
            # 오디오 에셋 생성
            audio_assets = []
            
            # 배경음악 생성
            background_music = self._generate_background_music(mood)
            audio_assets.append(background_music)
            
            # 효과음 생성
            sound_effects = self._generate_sound_effects(script)
            audio_assets.extend(sound_effects)
            
            # 나레이션 생성
            narration = self._generate_narration(script, mood)
            audio_assets.append(narration)
            
            # 캐시에 저장
            self._cache_audio(script_key, audio_assets)
            
            return audio_assets
        except Exception as e:
            print(f"오디오 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_audio()
    
    def _generate_background_music(self, mood: str) -> Dict:
        """배경음악을 생성합니다."""
        return {
            "type": AudioType.BACKGROUND_MUSIC.value,
            "content": f"background_music_{mood}.mp3",
            "timing": 0.0,
            "duration": 60.0,  # 전체 영상 길이
            "metadata": {
                "mood": mood,
                "volume": 0.3
            }
        }
    
    def _generate_sound_effects(self, script: str) -> List[Dict]:
        """효과음을 생성합니다."""
        effects = []
        current_time = 0.0
        
        for line in script.split('\n'):
            if "(효과음:" in line:
                effect_type = line.split(":")[1].strip(")")
                effects.append({
                    "type": AudioType.SOUND_EFFECT.value,
                    "content": f"sound_effect_{effect_type}.mp3",
                    "timing": current_time,
                    "duration": 0.5,
                    "metadata": {
                        "effect_type": effect_type,
                        "volume": 0.5
                    }
                })
            current_time += 0.5  # 대략적인 시간 추정
        
        return effects
    
    def _generate_narration(self, script: str, mood: str) -> Dict:
        """나레이션을 생성합니다."""
        try:
            # 나레이션용 텍스트 추출 (효과음 마커 제거)
            narration_text = "\n".join(
                line for line in script.split('\n')
                if not line.strip().startswith("(효과음:")
            )
            
            # 음성 설정
            voice_settings = VoiceSettings(
                stability=0.5,
                similarity_boost=0.75
            )
            
            # 기본 음성 선택 (나중에 사용자 설정으로 변경 가능)
            voice = Voice(
                voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                settings=voice_settings
            )
            
            # 오디오 생성
            audio = generate(
                text=narration_text,
                voice=voice
            )
            
            # 오디오 파일 저장
            file_path = os.path.join(
                self.audio_dir,
                f"narration_{mood}_{int(os.path.getmtime(self.storage_path))}.mp3"
            )
            
            with open(file_path, 'wb') as f:
                for chunk in audio:
                    if isinstance(chunk, bytes):
                        f.write(chunk)
            
            return {
                "type": AudioType.NARRATION.value,
                "content": file_path,
                "timing": 0.0,
                "duration": 60.0,  # 전체 영상 길이
                "metadata": {
                    "mood": mood,
                    "volume": 0.7
                }
            }
        except Exception as e:
            print(f"나레이션 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_narration()
    
    def _generate_dummy_audio(self) -> List[Dict]:
        """오류 발생 시 사용할 더미 오디오 에셋을 생성합니다."""
        return [
            self._generate_dummy_background_music(),
            self._generate_dummy_narration()
        ]
    
    def _generate_dummy_background_music(self) -> Dict:
        """더미 배경음악을 생성합니다."""
        return {
            "type": AudioType.BACKGROUND_MUSIC.value,
            "content": "dummy_background_music.mp3",
            "timing": 0.0,
            "duration": 60.0,
            "metadata": {
                "error": "Failed to generate background music"
            }
        }
    
    def _generate_dummy_narration(self) -> Dict:
        """더미 나레이션을 생성합니다."""
        return {
            "type": AudioType.NARRATION.value,
            "content": "dummy_narration.mp3",
            "timing": 0.0,
            "duration": 60.0,
            "metadata": {
                "error": "Failed to generate narration"
            }
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
        with open(self.storage_path, 'r') as f:
            return json.load(f)
    
    def _save_audio_data(self, audio_data: Dict):
        """오디오 데이터를 저장합니다."""
        with open(self.storage_path, 'w') as f:
            json.dump(audio_data, f, indent=2) 