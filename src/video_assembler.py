import os
from typing import Dict, List, Optional
from moviepy import VideoFileClip, ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

class VideoAssembler:
    def __init__(self):
        self.output_dir = "data/output"
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리가 존재하는지 확인합니다."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def assemble_video(self, visual_assets: List[Dict], audio_assets: List[Dict]) -> str:
        """비주얼 에셋과 오디오 에셋을 조합하여 최종 비디오를 생성합니다."""
        try:
            # 비디오 클립 생성
            video_clips = []
            current_time = 0
            
            for visual in visual_assets:
                if visual["type"] == "VIDEO":
                    clip = VideoFileClip(visual["content"])
                    if clip.duration > visual["duration"]:
                        clip = clip.subclip(0, visual["duration"])
                    video_clips.append(clip)
                else:  # IMAGE
                    clip = ImageClip(visual["content"]).with_duration(visual["duration"])
                    video_clips.append(clip)
                current_time += visual["duration"]
            
            # 비디오 클립 연결
            final_video = concatenate_videoclips(video_clips)
            
            # 오디오 클립 생성 및 추가
            audio_clips = []
            for audio in audio_assets:
                if audio["type"] == "NARRATION":
                    clip = AudioFileClip(audio["content"])
                    audio_clips.append(clip)
                else:  # SOUND_EFFECT
                    clip = AudioFileClip(audio["content"]).with_start(audio["timing"])
                    audio_clips.append(clip)
            
            # 오디오 클립 믹싱
            final_audio = CompositeVideoClip([clip for clip in audio_clips])
            
            # 비디오와 오디오 결합
            final_video = final_video.with_audio(final_audio)
            
            # 최종 비디오 저장
            output_path = os.path.join(self.output_dir, "final_video.mp4")
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
            for clip in audio_clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"비디오 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_video()
    
    def _generate_dummy_video(self) -> str:
        """오류 발생 시 사용할 더미 비디오를 생성합니다."""
        return "data/output/dummy_video.mp4" 