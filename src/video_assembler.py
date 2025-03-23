import os
import json
from typing import Dict, List, Optional
import ffmpeg
from PIL import Image

class VideoAssembler:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.output_dir = os.path.abspath(os.path.join("data", task_id, "output"))
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리가 존재하는지 확인합니다."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def assemble_video(self, content_id: str, content_data: Dict) -> str:
        """비디오를 조합하여 최종 비디오를 생성합니다."""
        try:
            # 임시 파일들을 저장할 디렉토리
            temp_dir = os.path.join(self.output_dir, "temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # 각 장면의 비디오 클립 생성
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
            
            # 각 클립을 임시 파일로 저장
            temp_files = []
            for i, clip in enumerate(video_clips):
                temp_file = os.path.join(temp_dir, f"clip_{i}.mp4")
                temp_files.append(temp_file)
                self._save_clip(clip, temp_file)
            
            # 최종 비디오 생성
            output_path = os.path.join(self.output_dir, f"{content_id}.mp4")
            self._concatenate_clips(temp_files, output_path)
            
            # 임시 파일 정리
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
            
            return output_path
            
        except Exception as e:
            print(f"Error occurred while generating video: {str(e)}")
            return self._generate_dummy_video()
    
    def _create_scene_clip(self, scene_name: str, scene_data: Dict) -> Optional[Dict]:
        """개별 장면의 비디오 클립을 생성합니다."""
        try:
            # 이미지 파일 경로 확인
            image_path = os.path.abspath(os.path.join("data", self.task_id, "images", f"{scene_name}.png"))
            if not os.path.exists(image_path):
                print(f"Can't find image file: {image_path}")
                raise Exception(f"Can't find image file: {image_path}")
            
            # 오디오 파일 경로 확인
            audio_path = os.path.abspath(os.path.join("data", self.task_id, "narration", f"{scene_name}.mp3"))
            if not os.path.exists(audio_path):
                print(f"Can't find audio file: {audio_path}")
                raise Exception(f"Can't find audio file: {audio_path}")
            
            # 오디오 파일의 길이 확인
            probe = ffmpeg.probe(audio_path)
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            duration = float(probe['format']['duration'])
            
            return {
                'image_path': image_path,
                'audio_path': audio_path,
                'duration': duration
            }
            
        except Exception as e:
            print(f"장면 클립 생성 중 오류 발생: {str(e)}")
            return None
    
    def _save_clip(self, clip: Dict, output_path: str):
        """개별 클립을 비디오 파일로 저장합니다."""
        try:
            # 이미지와 오디오를 결합하여 비디오 생성
            video = ffmpeg.input(clip['image_path'], loop=1, t=clip['duration'])
            audio = ffmpeg.input(clip['audio_path'])
            
            stream = (
                ffmpeg
                .output(
                    video,
                    audio,
                    output_path,
                    acodec='aac',
                    vcodec='libx264',
                    pix_fmt='yuv420p',
                    r=30,
                    ac=2,
                    ar='44100',
                    preset='medium',
                    crf=23,
                    vf='scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2'
                )
                .overwrite_output()
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
        except ffmpeg.Error as e:
            print(f"Error occurred while saving clip: {e.stderr.decode()}")
            raise
    
    def _concatenate_clips(self, clip_files: List[str], output_path: str):
        """여러 클립을 하나의 비디오로 연결합니다."""
        try:
            # concat demuxer를 위한 파일 목록 생성
            concat_file = os.path.join(os.path.dirname(output_path), "concat.txt")
            with open(concat_file, 'w') as f:
                for clip_file in clip_files:
                    f.write(f"file '{os.path.abspath(clip_file)}'\n")
            
            # 클립들을 연결
            stream = (
                ffmpeg
                .input(concat_file, format='concat', safe=0)
                .output(
                    output_path,
                    c='copy',
                    movflags='+faststart'
                )
                .overwrite_output()
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            # 임시 파일 삭제
            os.remove(concat_file)
            
        except ffmpeg.Error as e:
            print(f"Error occurred while concatenating clips: {e.stderr.decode()}")
            raise
    
    def _generate_dummy_video(self) -> str:
        """오류 발생 시 사용할 더미 비디오를 생성합니다."""
        dummy_path = os.path.join(self.output_dir, "dummy_video.mp4")
        if not os.path.exists(dummy_path):
            # 검은색 프레임 생성
            black_frame = Image.new('RGB', (720, 1280), 'black')
            temp_frame = os.path.join(self.output_dir, "temp_frame.png")
            black_frame.save(temp_frame)
            
            # 더미 비디오 생성
            stream = (
                ffmpeg
                .input(temp_frame, loop=1, t=1)
                .output(
                    dummy_path,
                    acodec='aac',
                    vcodec='libx264',
                    pix_fmt='yuv420p',
                    r=30,
                    preset='medium',
                    crf=23
                )
                .overwrite_output()
            )
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            
            # 임시 파일 삭제
            os.remove(temp_frame)
            
        return dummy_path 