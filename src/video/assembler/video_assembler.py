import ffmpeg
from typing import List, Dict, Optional
from ..utils.logger import Logger
from ..file.file_manager import FileManager
from ..scene.scene_generator import SceneGenerator
from ..audio.audio_processor import AudioProcessor

class VideoAssembler:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.logger = Logger()
        self.file_manager = FileManager(task_id)
        self.scene_generator = SceneGenerator()
        self.audio_processor = AudioProcessor()
    
    def create_scene(
        self,
        scene_number: int,
        text: str,
        duration: Optional[float] = None,
        transition_type: str = "fade"
    ) -> str:
        """개별 씬을 생성합니다."""
        try:
            # 이미지 경로 가져오기
            image_path = self.file_manager.get_image_path(scene_number)
            if not self.file_manager.file_exists(image_path):
                raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            
            # 오디오 경로 가져오기
            audio_path = self.file_manager.get_audio_path(scene_number)
            if not self.file_manager.file_exists(audio_path):
                raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_path}")
            
            output_path = self.file_manager.get_clip_path(scene_number)
            
            if transition_type:
                self.scene_generator.create_scene_with_transition(
                    image_path=image_path,
                    audio_path=audio_path,
                    text=text,
                    scene_number=scene_number,
                    output_path=output_path,
                    duration=duration,
                    transition_type=transition_type
                )
            else:
                self.scene_generator.create_scene(
                    image_path=image_path,
                    audio_path=audio_path,
                    text=text,
                    scene_number=scene_number,
                    output_path=output_path,
                    duration=duration
                )
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"씬 {scene_number} 생성 실패: {e}")
            raise
    
    def assemble_video(
        self,
        scenes: List[Dict],
        output_filename: str = "final_video.mp4",
        background_music: Optional[str] = None,
        volume: float = 0.3
    ) -> str:
        """모든 씬을 하나의 비디오로 조립합니다."""
        try:
            # 씬 파일 목록 생성
            scene_files = []
            for i, scene in enumerate(scenes, 1):
                scene_path = self.create_scene(
                    scene_number=i,
                    text=scene['text'],
                    duration=scene.get('duration'),
                    transition_type=scene.get('transition', 'fade')
                )
                scene_files.append(scene_path)
            
            # 최종 출력 경로
            output_path = self.file_manager.get_final_path(output_filename)
            
            # 씬 파일 목록 생성
            with open('temp_list.txt', 'w') as f:
                for scene_file in scene_files:
                    f.write(f"file '{scene_file}'\n")
            
            # 비디오 병합
            stream = ffmpeg.input('temp_list.txt', format='concat', safe=0)
            
            # 배경음악 추가
            if background_music:
                background = ffmpeg.input(background_music)
                stream = ffmpeg.filter([stream, background], 'amix', inputs=2, duration='first', dropout_transition=2)
            
            # 출력
            stream = ffmpeg.output(
                stream,
                output_path,
                vcodec='libx264',
                acodec='aac',
                pix_fmt='yuv420p',
                preset='medium',
                movflags='+faststart'
            )
            
            ffmpeg.run(stream, overwrite_output=True)
            
            # 임시 파일 정리
            import os
            os.remove('temp_list.txt')
            self.file_manager.cleanup()
            
            self.logger.info("비디오 조립 완료")
            return output_path
            
        except Exception as e:
            self.logger.error(f"비디오 조립 실패: {e}")
            raise 