import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
from enum import Enum

class AudioType(Enum):
    BACKGROUND_MUSIC = "background_music"
    SOUND_EFFECT = "sound_effect"
    NARRATION = "narration"

@dataclass
class SoundEffect:
    type: str  # e.g., "whoosh", "pop", "ding"
    timing: float  # start time in seconds
    duration: float  # duration in seconds
    volume: float  # 0.0 to 1.0

@dataclass
class AudioAsset:
    type: AudioType
    content: str  # prompt for music, text for narration, or effect type
    timing: float
    duration: float
    file_path: Optional[str] = None
    metadata: Optional[Dict] = None

class AudioGenerator:
    def __init__(self):
        self.storage_path = "data/audio.json"
        self.audio_dir = "data/audio_files"
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
        # 환경 변수 로드
        load_dotenv()
        
        # ElevenLabs API 키 확인
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            raise ValueError(
                "ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        try:
            # API 키 유효성 검사를 위해 사용 가능한 음성 목록 조회
            self.client = ElevenLabs(api_key=elevenlabs_api_key)
            available_voices = self.client.voices.get_all()
            print("ElevenLabs API 연결 성공!")
            print(f"사용 가능한 음성 수: {len(available_voices.voices)}")
        except Exception as e:
            raise ValueError(f"ElevenLabs API 키 검증 실패: {str(e)}")
    
    def generate_audio(self, script: str, mood: str) -> List[Dict]:
        """스크립트에 맞는 오디오를 생성합니다."""
        # 캐시 확인
        script_key = str(hash(script))
        cached_audio = self._get_cached_audio(script_key)
        if cached_audio:
            return cached_audio
        
        # 새로운 오디오 에셋 생성
        audio_assets = []
        
        # 1. 배경음악 정보 생성
        bg_music = self._generate_background_music(mood)
        audio_assets.append(bg_music)
        
        # 2. 효과음 생성
        sound_effects = self._generate_sound_effects(script)
        audio_assets.extend(sound_effects)
        
        # 3. 나레이션 생성
        narration = self._generate_narration(script)
        audio_assets.append(narration)
        
        # 캐시에 저장
        self._cache_audio(script_key, audio_assets)
        
        return audio_assets
    
    def _generate_background_music(self, mood: str) -> Dict:
        """배경음악 정보를 생성합니다."""
        return {
            "type": AudioType.BACKGROUND_MUSIC.value,
            "content": f"Background music in {mood} mood",
            "timing": 0.0,
            "duration": 60.0,  # 기본 지속 시간
            "metadata": {
                "mood": mood,
                "source": "youtube_music",
                "volume": 0.3  # 배경음악은 낮은 볼륨
            }
        }
    
    def _generate_sound_effects(self, script: str) -> List[Dict]:
        """효과음을 생성합니다."""
        effects = []
        current_time = 0.0
        
        # 스크립트에서 효과음 마커 파싱
        lines = script.split("\n")
        for line in lines:
            if "[SOUND:" in line:
                # 효과음 정보 추출
                effect_type = line[line.find(":")+1:line.find("]")]
                effects.append({
                    "type": AudioType.SOUND_EFFECT.value,
                    "content": effect_type,
                    "timing": current_time,
                    "duration": 0.5,  # 기본 효과음 지속 시간
                    "metadata": {
                        "effect_type": effect_type,
                        "volume": 0.7
                    }
                })
            current_time += 2.0  # 대략적인 타이밍
        
        return effects
    
    def _generate_narration(self, script: str) -> Dict:
        """나레이션을 생성합니다."""
        # 나레이션용 스크립트 정리
        narration_text = self._clean_script_for_narration(script)
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"narration_{timestamp}.mp3"
        filepath = os.path.join(self.audio_dir, filename)
        
        try:
            # ElevenLabs를 사용하여 오디오 생성
            audio = self.client.text_to_speech.convert(
                text=narration_text,
                voice_id="21m00Tcm4TlvDq8ikWAM",  # Josh voice
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            # 오디오 파일 저장
            with open(filepath, "wb") as f:
                f.write(audio)
            
            return {
                "type": AudioType.NARRATION.value,
                "content": narration_text,
                "timing": 0.0,
                "duration": len(narration_text.split()) * 0.3,  # 대략적인 지속 시간
                "file_path": filepath,
                "metadata": {
                    "voice": "Josh",
                    "model": "eleven_multilingual_v2",
                    "volume": 1.0
                }
            }
        except Exception as e:
            print(f"나레이션 생성 중 오류 발생: {str(e)}")
            # 오류 발생 시 더미 데이터 반환
            return {
                "type": AudioType.NARRATION.value,
                "content": narration_text,
                "timing": 0.0,
                "duration": 30.0,
                "file_path": None,
                "metadata": {
                    "error": str(e)
                }
            }
    
    def _clean_script_for_narration(self, script: str) -> str:
        """나레이션을 위해 스크립트를 정리합니다."""
        # 섹션 마커 제거
        script = script.replace("[HOOK]", "").replace("[CONTENT]", "").replace("[CONCLUSION]", "")
        
        # 효과음 마커 제거
        lines = script.split("\n")
        cleaned_lines = []
        for line in lines:
            if "[SOUND:" not in line:
                cleaned_lines.append(line)
        
        return " ".join(cleaned_lines)
    
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