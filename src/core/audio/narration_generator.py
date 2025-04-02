"""
나레이션 생성을 담당하는 NarrationGenerator 클래스

이 클래스는 ElevenLabs를 사용하여 각 장면의 스크립트를 음성으로 변환합니다.
주요 기능:
- 각 장면의 스크립트를 음성으로 변환
- 음성 파일 저장 및 관리
"""

from typing import Dict, List, Any
from ...utils.logger import Logger
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import time
import ffmpeg

class NarrationGenerator:
    def __init__(self, task_id: str, creator: str):
        self.logger = Logger()
        self.ELEVENLABS_API_KEY = "ELEVENLABS_API_KEY"
        self._setup_elevenlabs()
        self.task_id = task_id
        self.creator = creator
        self.base_dir = os.path.join("data", creator, task_id)
        self.narrations_dir = os.path.join(self.base_dir, "narrations")
        os.makedirs(self.narrations_dir, exist_ok=True)
    
    def _setup_elevenlabs(self):
        """Set up ElevenLabs API key."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        load_dotenv(os.path.join(project_root, '.env'))

        if not os.getenv(self.ELEVENLABS_API_KEY):
            raise ValueError(
                "ElevenLabs API key not found. Please set the ELEVENLABS_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        
        self.client = ElevenLabs(api_key=os.getenv(self.ELEVENLABS_API_KEY))
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """오디오 파일의 실제 길이를 측정합니다."""
        try:
            probe = ffmpeg.probe(audio_path)
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            return float(audio_info['duration'])
        except Exception as e:
            self.logger.error(f"Error getting audio duration: {str(e)}")
            raise
    
    def generate_narrations(self, content_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        콘텐츠 계획을 바탕으로 나레이션을 생성합니다.

        Args:
            content_plan (Dict[str, Any]): 콘텐츠 계획 정보

        Returns:
            Dict[str, Any]: 생성된 나레이션 정보
        """
        self.logger.section("Narration generation started")
        self.logger.info(f"Task ID: {self.task_id}")
        
        try:
            narrations = {
                "hook": self._generate_narration(content_plan["hook"], "hook"),
                "scenes": [],
                "conclusion": self._generate_narration(content_plan["conclusion"], "conclusion")
            }
            
            # Generate narration for each scene
            for i, scene in enumerate(content_plan["scenes"], 1):
                scene_narration = self._generate_narration(scene, f"scene_{i}")
                narrations["scenes"].append(scene_narration)
            
            self.logger.success("Narration generation completed successfully")
            return narrations
            
        except Exception as e:
            self.logger.error(f"Error generating narrations: {str(e)}")
            raise e
    
    def _generate_narration(self, scene: Dict[str, Any], scene_name: str) -> Dict[str, Any]:
        """
        개별 장면의 스크립트를 음성으로 변환합니다.

        Args:
            scene (Dict[str, Any]): 장면 정보
            scene_name (str): 장면 이름 (파일명에 사용)

        Returns:
            Dict[str, Any]: 생성된 음성 정보
        """
        try:
            # Generate audio using ElevenLabs
            self.logger.info(f"Generating narration for {scene_name}...")
            
            # Generate audio with exaggerated voice settings
            audio = self.client.text_to_speech.convert(
                text=scene["script"],
                voice_id="5Q0t7uMcjvnagumLfvZi",  # Josh voice
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.8,
                    "use_speaker_boost": True
                }
            )
            
            # Save audio file
            output_path = os.path.join(self.narrations_dir, f"{scene_name}.mp3")
            with open(output_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            
            # Get audio duration
            duration = self._get_audio_duration(output_path)
            
            self.logger.success(f"Narration saved: {output_path}")
            return {
                "scene_title": scene.get("title", ""),
                "audio_path": output_path,
                "duration": duration
            }
            
        except Exception as e:
            self.logger.error(f"Error generating narration: {str(e)}")
            raise e 