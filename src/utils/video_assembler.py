import os
from typing import Dict, Any, List
from moviepy.editor import VideoFileClip, ImageClip, TextClip, ColorClip, CompositeVideoClip, AudioFileClip
import json

class VideoAssembler:
    def __init__(self, image_dir: str, audio_dir: str):
        self.image_dir = image_dir
        self.audio_dir = audio_dir
    
    def _create_scene_video(self, scene: Dict[str, Any], output_path: str) -> None:
        """Create a video for a single scene"""
        try:
            # 비디오 설정
            width, height = 1080, 1920
            fps = 30
            duration = scene.get('duration', 5)
            
            # 비디오 생성
            video = VideoFileClip(None, width=width, height=height, fps=fps, duration=duration)
            
            # 배경 이미지 로드
            if scene['type'] == 'hook':
                background_path = os.path.join(self.image_dir, 'hook', f"{scene['image_style_name']}.png")
            elif scene['type'] == 'conclusion':
                background_path = os.path.join(self.image_dir, 'conclusion', f"{scene['image_style_name']}.png")
            else:
                background_path = os.path.join(self.image_dir, 'content', f"{scene['image_style_name']}.png")
            
            if not os.path.exists(background_path):
                raise FileNotFoundError(f"Background image not found: {background_path}")
            
            # 배경 이미지 로드 및 크기 조정
            background = ImageClip(background_path)
            background = background.resize((width, height))
            
            # 자막 텍스트 설정
            text = scene.get('caption', '')
            font_size = 60
            font = "Noto Sans CJK KR"  # 이모지를 지원하는 폰트로 변경
            
            # 자막 배경 박스 설정
            padding = 20
            text_clip = TextClip(
                text,
                fontsize=font_size,
                font=font,
                color='white',
                size=(width - 100, None),  # 가로 여백 50픽셀
                method='caption',
                align='center'
            )
            
            # 자막 배경 박스 생성
            text_width = text_clip.w
            text_height = text_clip.h
            box_width = text_width + (padding * 2)
            box_height = text_height + (padding * 2)
            
            # 배경 박스 생성 (반투명)
            box = ColorClip(size=(box_width, box_height), color=(0, 0, 0))
            box = box.set_opacity(0.4)  # 투명도 70%
            
            # 자막과 배경 박스 위치 설정
            box = box.set_position(('center', 'bottom'))
            text_clip = text_clip.set_position(('center', 'bottom'))
            
            # 비디오 합성
            final = CompositeVideoClip([
                background,
                box,
                text_clip
            ])
            
            # 오디오 추가
            if scene.get('audio_path'):
                audio = AudioFileClip(scene['audio_path'])
                final = final.set_audio(audio)
            
            # 비디오 저장
            final.write_videofile(
                output_path,
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                threads=4
            )
            
            # 리소스 정리
            final.close()
            if scene.get('audio_path'):
                audio.close()
            
        except Exception as e:
            print(f"Error creating scene video: {str(e)}")
            raise 