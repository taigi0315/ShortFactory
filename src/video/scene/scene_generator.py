import ffmpeg
from typing import Optional, Tuple
from ..utils.logger import Logger
from ..text.text_renderer import TextRenderer
from ..audio.audio_processor import AudioProcessor

class SceneGenerator:
    def __init__(self):
        self.logger = Logger()
        self.text_renderer = TextRenderer()
        self.audio_processor = AudioProcessor()
    
    def create_scene(
        self,
        image_path: str,
        audio_path: str,
        text: str,
        scene_number: int,
        output_path: str,
        duration: Optional[float] = None
    ) -> None:
        """이미지, 오디오, 텍스트를 조합하여 씬을 생성합니다."""
        try:
            # 오디오 길이 확인
            if duration is None:
                duration = self.audio_processor.get_audio_duration(audio_path)
            
            # 텍스트 필터 생성
            text_filter = self.text_renderer.create_scene_text_filter(text, scene_number)
            
            # 비디오 스트림 생성
            stream = ffmpeg.input(image_path, loop=1, t=duration)
            
            # 텍스트 추가
            stream = ffmpeg.filter(stream, text_filter)
            
            # 오디오 스트림 추가
            audio = ffmpeg.input(audio_path)
            
            # 출력
            stream = ffmpeg.output(
                stream,
                audio,
                output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                preset='medium',
                movflags='+faststart'
            )
            
            ffmpeg.run(stream, overwrite_output=True)
            self.logger.info(f"씬 {scene_number} 생성 완료")
            
        except Exception as e:
            self.logger.error(f"씬 {scene_number} 생성 실패: {e}")
            raise
    
    def create_scene_with_transition(
        self,
        image_path: str,
        audio_path: str,
        text: str,
        scene_number: int,
        output_path: str,
        duration: Optional[float] = None,
        transition_type: str = "fade"
    ) -> None:
        """전환 효과가 있는 씬을 생성합니다."""
        try:
            if duration is None:
                duration = self.audio_processor.get_audio_duration(audio_path)
            
            # 전환 시간 설정 (1초)
            transition_duration = 1.0
            
            # 텍스트 필터 생성
            text_filter = self.text_renderer.create_scene_text_filter(text, scene_number)
            
            # 비디오 스트림 생성
            stream = ffmpeg.input(image_path, loop=1, t=duration)
            
            # 전환 효과 추가
            if transition_type == "fade":
                stream = ffmpeg.filter(stream, 'fade', t='in', st=0, d=transition_duration)
                stream = ffmpeg.filter(stream, 'fade', t='out', st=duration-transition_duration, d=transition_duration)
            elif transition_type == "zoom":
                stream = ffmpeg.filter(stream, 'zoompan', z='1.5', d=duration*25)
            
            # 텍스트 추가
            stream = ffmpeg.filter(stream, text_filter)
            
            # 오디오 스트림 추가
            audio = ffmpeg.input(audio_path)
            
            # 출력
            stream = ffmpeg.output(
                stream,
                audio,
                output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                preset='medium',
                movflags='+faststart'
            )
            
            ffmpeg.run(stream, overwrite_output=True)
            self.logger.info(f"전환 효과가 있는 씬 {scene_number} 생성 완료")
            
        except Exception as e:
            self.logger.error(f"전환 효과가 있는 씬 {scene_number} 생성 실패: {e}")
            raise 