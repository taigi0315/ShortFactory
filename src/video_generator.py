import os
import json
from typing import Dict, List, Optional
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from .utils.logger import Logger

class VideoGenerator:
    def __init__(self):
        self.output_dir = "data/output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = Logger()
    
    def generate_video(self, script: Dict, visual_assets: List[Dict], audio_assets: List[Dict]) -> str:
        """스크립트, 시각적 에셋, 오디오 에셋을 사용하여 최종 비디오를 생성합니다."""
        self.logger.section("비디오 생성 시작")
        self.logger.info(f"스크립트: {json.dumps(script, ensure_ascii=False)}")
        self.logger.info(f"시각적 에셋 수: {len(visual_assets)}")
        self.logger.info(f"오디오 에셋 수: {len(audio_assets)}")
        
        try:
            # 비디오 클립 생성
            self.logger.subsection("비디오 클립 생성")
            video_clips = []
            
            for i, (visual, audio) in enumerate(zip(visual_assets, audio_assets), 1):
                self.logger.process(f"클립 {i} 생성 중...")
                self.logger.info(f"시각적 에셋: {visual['content']}")
                self.logger.info(f"오디오 에셋: {audio['content']}")
                
                # 시각적 클립 생성
                if visual["type"] == "image":
                    visual_clip = ImageClip(visual["content"]).set_duration(audio["duration"])
                else:  # video
                    visual_clip = VideoFileClip(visual["content"]).subclip(0, audio["duration"])
                
                # 오디오 클립 생성
                audio_clip = AudioFileClip(audio["content"])
                
                # 클립 합성
                clip = visual_clip.set_audio(audio_clip)
                video_clips.append(clip)
                self.logger.success(f"클립 {i} 생성 완료")
            
            # 모든 클립 연결
            self.logger.process("모든 클립 연결 중...")
            final_video = concatenate_videoclips(video_clips)
            
            # 최종 비디오 저장
            output_path = f"{self.output_dir}/final_video.mp4"
            self.logger.process(f"최종 비디오 저장 중... ({output_path})")
            final_video.write_videofile(
                output_path,
                fps=30,
                codec="libx264",
                audio_codec="aac"
            )
            
            # 리소스 정리
            self.logger.process("리소스 정리 중...")
            final_video.close()
            for clip in video_clips:
                clip.close()
            
            self.logger.success(f"비디오 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"비디오 생성 중 오류 발생: {str(e)}")
            return self._generate_dummy_video()
    
    def _generate_dummy_video(self) -> str:
        """오류 발생 시 사용할 더미 비디오를 생성합니다."""
        try:
            self.logger.process("더미 비디오 생성 중...")
            
            # 검은 화면 이미지 생성
            import numpy as np
            from PIL import Image
            
            black_screen = np.zeros((1080, 1920, 3), dtype=np.uint8)
            image = Image.fromarray(black_screen)
            
            # 임시 이미지 저장
            temp_image_path = f"{self.output_dir}/temp_black_screen.png"
            os.makedirs(os.path.dirname(temp_image_path), exist_ok=True)
            image.save(temp_image_path)
            
            # 무음 파일 생성
            import wave
            temp_audio_path = f"{self.output_dir}/temp_silence.wav"
            
            with wave.open(temp_audio_path, "w") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                wav_file.writeframes(b"\x00" * 44100 * 2)  # 2초 길이의 무음
            
            # 더미 비디오 생성
            output_path = f"{self.output_dir}/dummy_video.mp4"
            
            # 이미지 클립 생성
            image_clip = ImageClip(temp_image_path).set_duration(2)
            
            # 오디오 클립 생성
            audio_clip = AudioFileClip(temp_audio_path)
            
            # 클립 합성
            final_clip = image_clip.set_audio(audio_clip)
            
            # 비디오 저장
            final_clip.write_videofile(
                output_path,
                fps=30,
                codec="libx264",
                audio_codec="aac"
            )
            
            # 리소스 정리
            final_clip.close()
            image_clip.close()
            audio_clip.close()
            
            # 임시 파일 삭제
            os.remove(temp_image_path)
            os.remove(temp_audio_path)
            
            self.logger.success(f"더미 비디오 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"더미 비디오 생성 중 오류 발생: {str(e)}")
            return f"{self.output_dir}/dummy_video.mp4" 