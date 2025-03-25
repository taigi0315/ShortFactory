import platform
import yaml
from typing import List
from ..utils.logger import Logger

class TextRenderer:
    def __init__(self):
        self.logger = Logger()
        self.config = self._load_config()
        self.font_path = self._get_system_font_path()
    
    def _load_config(self) -> dict:
        """설정 파일을 로드합니다."""
        try:
            with open('config/video_config.yaml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"설정 파일 로드 실패: {e}")
            return {}
    
    def _get_system_font_path(self) -> str:
        """시스템에 맞는 폰트 경로를 반환합니다."""
        system = platform.system().lower()
        return self.config.get('fonts', {}).get(system, self.config.get('fonts', {}).get('default', 'Arial'))
    
    def escape_special_chars(self, text: str) -> str:
        """ffmpeg drawtext 필터에서 사용할 수 있도록 특수문자를 이스케이프합니다."""
        special_chars = self.config.get('special_chars', [])
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
        return text
    
    def create_text_filter(self, text: str, position: str = "center") -> str:
        """텍스트 필터 문자열을 생성합니다."""
        text_settings = self.config.get('text_settings', {})
        escaped_text = self.escape_special_chars(text)
        
        filter_str = (
            f"drawtext=text='{escaped_text}'"
            f":fontfile='{self.font_path}'"
            f":fontsize={text_settings.get('font_size', 48)}"
            f":fontcolor={text_settings.get('font_color', 'white')}"
            f":x=(w-text_w)/2"
            f":y=(h-text_h)/2"
            f":box=1"
            f":boxcolor=black@0.5"
            f":boxborderw=5"
            f":line_spacing=10"
            f":text_align={text_settings.get('alignment', 'center')}"
        )
        
        return filter_str
    
    def create_scene_text_filter(self, text: str, scene_number: int) -> str:
        """씬 번호와 텍스트를 포함하는 필터 문자열을 생성합니다."""
        scene_text = f"Scene {scene_number}"
        scene_filter = self.create_text_filter(scene_text, "top")
        text_filter = self.create_text_filter(text, "center")
        return f"{scene_filter},{text_filter}" 