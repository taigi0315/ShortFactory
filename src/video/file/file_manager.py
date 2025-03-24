import os
from typing import Optional
from ..utils.logger import Logger

class FileManager:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.base_dir = os.path.join("data", task_id)
        self.output_dir = os.path.join(self.base_dir, "output")
        self.clips_dir = os.path.join(self.output_dir, "clips")
        self.final_dir = os.path.join(self.output_dir, "final")
        self.images_dir = os.path.join(self.base_dir, "images")
        self.audio_dir = os.path.join(self.base_dir, "audio")
        self.narration_dir = os.path.join(self.base_dir, "narration")
        self.logger = Logger()
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """필요한 디렉토리들을 생성합니다."""
        directories = [
            self.output_dir,
            self.clips_dir,
            self.final_dir,
            self.images_dir,
            self.audio_dir,
            self.narration_dir
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_clip_path(self, scene_number: int) -> str:
        """특정 씬의 클립 파일 경로를 반환합니다."""
        return os.path.join(self.clips_dir, f"scene_{scene_number}.mp4")
    
    def get_final_path(self, filename: str) -> str:
        """최종 출력 파일의 경로를 반환합니다."""
        return os.path.join(self.final_dir, filename)
    
    def get_image_path(self, scene_number: int) -> str:
        """특정 씬의 이미지 파일 경로를 반환합니다."""
        return os.path.join(self.images_dir, f"scene_{scene_number}.png")
    
    def get_audio_path(self, scene_number: int) -> str:
        """특정 씬의 오디오 파일 경로를 반환합니다."""
        return os.path.join(self.audio_dir, f"scene_{scene_number}.mp3")
    
    def get_narration_path(self, scene_number: int) -> str:
        """특정 씬의 나레이션 파일 경로를 반환합니다."""
        return os.path.join(self.narration_dir, f"scene_{scene_number}.mp3")
    
    def file_exists(self, filepath: str) -> bool:
        """파일이 존재하는지 확인합니다."""
        return os.path.exists(filepath)
    
    def remove_file(self, filepath: str) -> None:
        """파일을 삭제합니다."""
        if self.file_exists(filepath):
            os.remove(filepath)
            self.logger.info(f"파일 삭제됨: {filepath}")
    
    def cleanup(self) -> None:
        """임시 파일들을 정리합니다."""
        # 클립 파일 정리
        for filename in os.listdir(self.clips_dir):
            if filename.endswith('.mp4'):
                self.remove_file(os.path.join(self.clips_dir, filename))
        
        # 임시 오디오 파일 정리
        for filename in os.listdir(self.audio_dir):
            if filename.endswith('.temp'):
                self.remove_file(os.path.join(self.audio_dir, filename)) 