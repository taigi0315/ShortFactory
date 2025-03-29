import os
from typing import Dict, Any
from core.logger import Logger
from core.tts_generator import TTSGenerator

class NarrationGenerator:
    def __init__(self, task_id: str, creator: str):
        self.task_id = task_id
        self.creator = creator
        self.base_dir = os.path.join("data", creator, task_id)
        self.audio_dir = os.path.join(self.base_dir, "audio")
        
        # 디렉토리 생성
        os.makedirs(self.audio_dir, exist_ok=True)
        
        self.logger = Logger()
        self.tts_generator = TTSGenerator()
    
    def create_narrations(self, content_plan: Dict[str, Any]) -> Dict[str, Any]:
        """콘텐츠 플랜에 따라 내레이션을 생성합니다."""
        try:
            # Hook 내레이션 생성
            if "hook" in content_plan:
                hook_audio = self._create_scene_narration(content_plan["hook"], "hook")
                content_plan["hook"]["audio_path"] = hook_audio
            
            # 각 씬별 내레이션 생성
            for scene in content_plan["scenes"]:
                scene_audio = self._create_scene_narration(scene, f"scene_{scene.get('scene_number', 1)}")
                scene["audio_path"] = scene_audio
            
            # Conclusion 내레이션 생성
            if "conclusion" in content_plan:
                conclusion_audio = self._create_scene_narration(content_plan["conclusion"], "conclusion")
                content_plan["conclusion"]["audio_path"] = conclusion_audio
            
            return content_plan
            
        except Exception as e:
            self.logger.error(f"Error creating narrations: {str(e)}")
            raise
    
    def _create_scene_narration(self, scene: Dict[str, Any], scene_id: str) -> str:
        """개별 씬의 내레이션을 생성합니다."""
        try:
            # 내레이션 생성
            audio_data = self.tts_generator.generate_speech(
                scene.get("script", ""),
                voice=scene.get("voice_name", "default")
            )
            
            # 오디오 저장
            output_path = os.path.join(self.audio_dir, f"{scene_id}.mp3")
            with open(output_path, "wb") as f:
                f.write(audio_data)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error creating scene narration: {str(e)}")
            raise 