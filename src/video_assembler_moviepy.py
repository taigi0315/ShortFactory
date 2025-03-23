import os
from typing import Dict, List, Optional
import numpy as np
from moviepy import VideoFileClip, ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image

class VideoAssembler:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.output_dir = os.path.join("data", task_id, "output")
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리가 존재하는지 확인합니다."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def assemble_video(self, content_id: str, content_data: Dict) -> str:
        """비디오를 조합하여 최종 비디오를 생성합니다."""
        try:
            # 비디오 클립 생성
            video_clips = []
            
            # Hook scene
            hook_clip = self._create_scene_clip(scene_name="hook", scene_data=content_data["hook"])
            if hook_clip:
                video_clips.append(hook_clip)
            
            # Main scenes
            for idx, scene_data in enumerate(content_data["scenes"]):
                scene_clip = self._create_scene_clip(scene_name=f"scene_{idx+1}", scene_data=scene_data)
                if scene_clip:
                    video_clips.append(scene_clip)
            
            # Conclusion scene
            conclusion_clip = self._create_scene_clip(scene_name="conclusion", scene_data=content_data["conclusion"])
            if conclusion_clip:
                video_clips.append(conclusion_clip)
            
            if not video_clips:
                return self._generate_dummy_video()
            
            # 비디오 클립 연결
            final_video = concatenate_videoclips(video_clips)
            
            # 최종 비디오 저장
            output_path = os.path.join(self.output_dir, f"{content_id}.mp4")
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac'
            )
            
            # 클립 정리
            final_video.close()
            for clip in video_clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error occurred while generating video: {str(e)}")
            return self._generate_dummy_video()
    
    def _create_scene_clip(self, scene_name: str, scene_data: Dict) -> Optional[VideoFileClip]:
        """개별 장면의 비디오 클립을 생성합니다."""
        try:
            # 이미지 클립 생성
            image_path = os.path.join("data", self.task_id, "images", f"{scene_name}.png")

            if not image_path or not os.path.exists(image_path):
                print(f"Can't find image file: {image_path}")
                raise Exception(f"Can't find image file: {image_path}")
            
            # 오디오 파일 경로 생성 및 확인
            audio_path = os.path.join("data", self.task_id, "narration", f"{scene_name}.mp3")
            if not os.path.exists(audio_path):
                print(f"Can't find audio file: {audio_path}")
                raise Exception(f"Can't find audio file: {audio_path}")
                
            # 오디오 클립 생성
            audio_clip = AudioFileClip(audio_path)
            
            # 이미지 로드 및 크기 조정
            img = Image.open(image_path)
            # 이미지를 16:9 비율로 조정 (1280x720)
            img = img.convert('RGB')
            # No need to update the image size since it comes as 16:9 ratio
            # img = img.resize((720, 1280), Image.Resampling.LANCZOS)
            
            # 이미지 클립 생성 및 오디오 길이만큼 지속 시간 설정
            image_clip = ImageClip(np.array(img)).with_duration(audio_clip.duration)
            
            # 이미지와 오디오 결합
            video_clip = image_clip.with_audio(audio_clip)
            
            return video_clip
            
        except Exception as e:
            print(f"장면 클립 생성 중 오류 발생: {str(e)}")
            return None
    
    def _generate_dummy_video(self) -> str:
        """오류 발생 시 사용할 더미 비디오를 생성합니다."""
        dummy_path = os.path.join(self.output_dir, "dummy_video.mp4")
        if not os.path.exists(dummy_path):
            dummy_clip = self._generate_dummy_clip()
            dummy_clip.write_videofile(
                dummy_path,
                fps=30,
                codec='libx264',
                audio_codec='aac'
            )
            dummy_clip.close()
        return dummy_path
    
    def _generate_dummy_clip(self) -> VideoFileClip:
        """더미 비디오 클립을 생성합니다."""
        # 검은색 프레임 생성 (1초)
        black_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        return ImageClip(black_frame).with_duration(1) 