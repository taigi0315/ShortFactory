import os
from typing import List, Dict
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.AudioClip import CompositeAudioClip
from PIL import Image
import numpy as np

class VideoAssembler:
    def __init__(self):
        self.output_dir = "data/output"
        self.total_duration = 0  # 전체 비디오 길이를 저장할 속성 추가
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """출력 디렉토리가 존재하는지 확인하고 없으면 생성합니다."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def assemble_video(self, script: str, visual_assets: List[Dict], audio_assets: List[Dict]) -> str:
        """최종 비디오를 생성합니다."""
        try:
            # 1. 비디오 클립 생성
            video_clips = self._create_video_clips(visual_assets)
            
            # 전체 비디오 길이 계산
            self.total_duration = sum(clip.duration for clip in video_clips)
            
            # 2. 오디오 트랙 생성
            audio_tracks = self._create_audio_tracks(audio_assets)
            
            # 3. 비디오와 오디오 결합
            final_video = self._combine_video_and_audio(video_clips, audio_tracks)
            
            # 4. 최종 비디오 저장
            output_path = self._save_final_video(final_video)
            
            return output_path
            
        except Exception as e:
            print(f"비디오 생성 중 오류 발생: {str(e)}")
            raise
    
    def _create_video_clips(self, visual_assets: List[Dict]) -> List[VideoFileClip]:
        """시각적 에셋을 비디오 클립으로 변환합니다."""
        clips = []
        
        for asset in visual_assets:
            try:
                if asset["type"] == "image":
                    # 이미지를 비디오 클립으로 변환
                    clip = self._create_image_clip(asset)
                elif asset["type"] == "video":
                    # 비디오 파일을 클립으로 변환
                    clip = VideoFileClip(asset["content"]).with_duration(asset["duration"])
                else:
                    raise ValueError(f"지원하지 않는 시각적 에셋 타입: {asset['type']}")
                
                # 클립의 시작 시간 설정
                clip = clip.with_start(asset["timing"])
                clips.append(clip)
                
            except Exception as e:
                print(f"클립 생성 중 오류 발생: {str(e)}")
                raise
        
        return clips
    
    def _create_image_clip(self, asset: Dict) -> ImageClip:
        """이미지를 비디오 클립으로 변환합니다."""
        try:
            # 이미지 로드
            image = Image.open(asset["content"])
            
            # 이미지를 numpy 배열로 변환
            image_array = np.array(image)
            
            # 이미지 클립 생성
            clip = ImageClip(image_array, duration=asset["duration"])
            
            return clip
            
        except Exception as e:
            print(f"이미지 클립 생성 중 오류 발생: {str(e)}")
            raise
    
    def _create_audio_tracks(self, audio_assets: List[Dict]) -> List[AudioFileClip]:
        """오디오 트랙 생성"""
        audio_tracks = []
        
        for asset in audio_assets:
            try:
                # 오디오 파일 로드
                audio = AudioFileClip(asset["content"])
                
                # 오디오 타입에 따른 처리
                if asset["type"] == "NARRATION":
                    # 나레이션은 원본 길이 유지
                    pass
                
                elif asset["type"] == "SOUND_EFFECT":
                    # 효과음은 지정된 시간에 재생
                    audio = audio.with_start(asset["timing"])
                
                else:
                    raise ValueError(f"지원하지 않는 오디오 타입입니다: {asset['type']}")
                
                audio_tracks.append(audio)
                
            except Exception as e:
                print(f"오디오 트랙 생성 중 오류 발생: {str(e)}")
                raise
        
        return audio_tracks
    
    def _combine_video_and_audio(self, video_clips: List[VideoFileClip], audio_tracks: List[AudioFileClip]) -> CompositeVideoClip:
        """비디오와 오디오를 결합합니다."""
        try:
            # 비디오 클립 결합
            final_video = CompositeVideoClip(video_clips)
            
            # 오디오 트랙 결합
            final_audio = CompositeAudioClip(audio_tracks)
            
            # 비디오에 오디오 설정
            final_video = final_video.with_audio(final_audio)
            
            return final_video
            
        except Exception as e:
            print(f"비디오와 오디오 결합 중 오류 발생: {str(e)}")
            raise
    
    def _save_final_video(self, video: CompositeVideoClip) -> str:
        """최종 비디오를 파일로 저장합니다."""
        try:
            # 출력 파일 경로 생성
            output_path = os.path.join(self.output_dir, "final_video.mp4")
            
            # 비디오 저장
            video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile="temp-audio.m4a",
                remove_temp=True
            )
            
            return output_path
            
        except Exception as e:
            print(f"비디오 저장 중 오류 발생: {str(e)}")
            raise 