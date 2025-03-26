import os
import json
from typing import Dict, List, Optional, Any
import ffmpeg
from PIL import Image
from .utils.logger import Logger
import platform
import re

class VideoAssembler:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.base_dir = os.path.join("data", task_id)
        self.output_dir = os.path.join(self.base_dir, "output")
        self.clips_dir = os.path.join(self.output_dir, "clips")
        self.final_dir = os.path.join(self.output_dir, "final")
        self.images_dir = os.path.join(self.base_dir, "images")
        
        # 디렉토리 생성
        os.makedirs(self.clips_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)
        
        self.logger = Logger()
        self._ensure_storage_exists()
        
        # 시스템 폰트 경로 설정
        self.font_path = self._get_system_font_path()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리가 존재하는지 확인합니다."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _get_system_font_path(self) -> str:
        """시스템에 따라 적절한 폰트 경로를 반환합니다."""
        system = platform.system().lower()
        if system == "darwin":  # macOS
            # 한글 폰트 우선 시도
            korean_fonts = [
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",
                "/Library/Fonts/AppleGothic.ttf",
                "/System/Library/Fonts/Supplemental/NanumGothic.ttf"
            ]
            for font in korean_fonts:
                if os.path.exists(font):
                    return font
            return "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
        elif system == "linux":
            # 한글 폰트 우선 시도
            korean_fonts = [
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
            ]
            for font in korean_fonts:
                if os.path.exists(font):
                    return font
            return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        elif system == "windows":
            # 한글 폰트 우선 시도
            korean_fonts = [
                "C:\\Windows\\Fonts\\malgun.ttf",
                "C:\\Windows\\Fonts\\gulim.ttc"
            ]
            for font in korean_fonts:
                if os.path.exists(font):
                    return font
            return "C:\\Windows\\Fonts\\arial.ttf"
        else:
            return "Arial"  # 폰트 이름만 지정
    
    def _escape_special_chars(self, text: str) -> str:
        """ffmpeg drawtext 필터에서 사용할 수 있도록 특수문자를 이스케이프합니다."""
        # 이스케이프해야 할 특수문자들
        special_chars = ['\\', ':', ';', ',', '=', '\\[', '\\]', '\\{', '\\}', '\\|', '\\?', '\\*', '\\+', '\\-', '\\/', '\\^', '\\$', '\\#', '\\@', '\\&', '\\%', '\\!', '\\~', '\\`', '\\"', '\\\'', '\\<', '\\>']
        
        # 각 특수문자를 이스케이프 처리
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
            
        return text
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """오디오 파일의 실제 길이를 측정합니다."""
        try:
            probe = ffmpeg.probe(audio_path)
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            return float(audio_info['duration'])
        except Exception as e:
            self.logger.error(f"Error getting audio duration: {str(e)}")
            raise
    
    def _create_scene_video(self, scene: Dict[str, Any], scene_index: int, scene_type: str = None) -> str:
        """개별 씬 비디오를 생성합니다."""
        if scene_type:
            scene_id = scene_type
        else:
            scene_id = f"scene_{scene.get('scene_number', scene_index)}"
        
        # 이미지와 오디오 파일 경로 생성
        image_path = os.path.join(self.base_dir, "images", f"{scene_id}.png")
        audio_path = os.path.join(self.base_dir, "narration", f"{scene_id}.mp3")
        
        caption = scene.get("caption", "")
        
        # 파일 존재 여부 확인
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"오디오 파일을 찾을 수 없습니다: {audio_path}")
        
        # 오디오 파일의 실제 길이 측정
        duration = self._get_audio_duration(audio_path)
        self.logger.info(f"Audio duration for {scene_id}: {duration} seconds")
        
        # 자막 텍스트 이스케이프 처리
        escaped_caption = self._escape_special_chars(caption)
        
        # 자막을 여러 줄로 분할 (한글은 한 줄당 최대 20자)
        max_chars_per_line = 20
        # 한글 문장 분리를 위한 정규식
        pattern = re.compile(r'.{1,%d}(?:\s|$)' % max_chars_per_line)
        lines = pattern.findall(caption.strip())
        lines = [line.strip() for line in lines if line.strip()]
        
        # 자막 필터 생성
        drawtext_filters = []
        for i, line in enumerate(lines):
            escaped_line = self._escape_special_chars(line)
            y_position = 1000 + (i * 50)  # 각 줄마다 50픽셀 간격 (한글은 더 큰 간격 필요)
            drawtext_filters.append({
                'text': escaped_line,
                'fontfile': self.font_path,
                'fontsize': '45',
                'fontcolor': 'white',
                'alpha': '0.9',
                'x': '(w-text_w)/2',
                'y': str(y_position),
                'box': '1',
                'boxcolor': 'black@0.5',  # 투명도 조정
                'boxborderw': '10',  # 박스 테두리 두께 증가
                'line_spacing': '15',  # 줄 간격 증가
                'enable': f"between(t,0,{duration})"
            })
        
        # 비디오 생성
        output_path = os.path.join(self.clips_dir, f"{scene_id}.mp4")
        
        try:
            # 입력 스트림 설정
            image = ffmpeg.input(image_path, loop=1, t=duration)
            audio = ffmpeg.input(audio_path)
            
            # 비디오 스트림 처리
            video = image.filter('scale', 720, 1280, force_original_aspect_ratio='decrease')
            video = video.filter('pad', 720, 1280, '(ow-iw)/2', '(oh-ih)/2')
            
            # 자막 추가
            for drawtext_filter in drawtext_filters:
                video = video.filter('drawtext', **drawtext_filter)
            
            video = video.filter('format', 'yuv420p')
            
            # 오디오 스트림 처리
            audio = audio.filter('aformat', sample_fmts='fltp', sample_rates='44100', channel_layouts='stereo')
            
            # 비디오 생성
            try:
                process = (
                    ffmpeg
                    .output(
                        video,
                        audio,
                        output_path,
                        acodec="aac",
                        vcodec="libx264",
                        preset="medium",
                        movflags="+faststart",
                        pix_fmt="yuv420p",
                        r=30,
                        ac=2,
                        ar="44100",
                        strict="-2",
                        audio_bitrate="192k",
                        shortest=None,  # 가장 짧은 스트림에 맞춤
                        max_interleave_delta="0"  # 오디오 싱크 개선
                    )
                    .overwrite_output()
                )
                
                # 명령어 출력
                print(" ".join(process.get_args()))
                
                # 실행
                process.run(capture_stdout=True, capture_stderr=True)
                
                return output_path
                
            except ffmpeg.Error as e:
                print(f"FFmpeg error: {e.stderr.decode()}")
                raise
            except Exception as e:
                print(f"Error creating scene video: {str(e)}")
                raise
            
        except ffmpeg.Error as e:
            print(f"FFmpeg error: {e.stderr.decode()}")
            raise
        except Exception as e:
            print(f"Error creating scene video: {str(e)}")
            raise
            
    def assemble_video(self, content_id: str, content_data: Dict[str, Any]) -> str:
        """최종 비디오를 조립합니다."""
        try:
            # 각 씬별 비디오 생성
            scene_videos = []
            
            # Hook 처리
            if "hook" in content_data:
                hook_video = self._create_scene_video(content_data["hook"], 0, "hook")
                scene_videos.append(hook_video)
            
            # 메인 씬 처리
            for i, scene in enumerate(content_data["scenes"]):
                scene_video = self._create_scene_video(scene, i+1)
                scene_videos.append(scene_video)
            
            # Conclusion 처리
            if "conclusion" in content_data:
                conclusion_video = self._create_scene_video(content_data["conclusion"], len(content_data["scenes"]), "conclusion")
                scene_videos.append(conclusion_video)
            
            # 씬 목록 파일 생성
            list_file = os.path.join(self.clips_dir, "scenes.txt")
            with open(list_file, "w", encoding='utf-8') as f:
                for video in scene_videos:
                    f.write(f"file '{os.path.abspath(video)}'\n")
            
            # 최종 비디오 생성
            output_path = os.path.join(self.final_dir, f"{content_id}.mp4")
            
            try:
                process = (
                    ffmpeg
                    .input(list_file, format='concat', safe=0)
                    .output(
                        output_path,
                        c='copy',
                        movflags='+faststart',
                        acodec='aac',
                        vcodec='libx264',
                        ac=2,
                        ar='44100',
                        strict='-2'
                    )
                    .overwrite_output()
                )
                
                # 명령어 출력
                print(" ".join(process.get_args()))
                
                # 실행
                process.run(capture_stdout=True, capture_stderr=True)
                
                return output_path
                
            except ffmpeg.Error as e:
                print(f"FFmpeg error: {e.stderr.decode()}")
                raise
            except Exception as e:
                print(f"Error creating final video: {str(e)}")
                raise
            
        except Exception as e:
            print(f"Error assembling video: {str(e)}")
            raise
    
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

    def _create_clip(self, image_path: str, audio_path: str, duration: int, text: str, output_path: str):
        """Create a video clip from an image and audio file."""
        stream = ffmpeg.input(image_path, loop=1, t=duration)
        audio = ffmpeg.input(audio_path)
        
        stream = ffmpeg.filter(stream, 'scale', 720, 1280, force_original_aspect_ratio='decrease')
        stream = ffmpeg.filter(stream, 'pad', 720, 1280, '(ow-iw)/2', '(oh-ih)/2')
        
        # Add text overlay
        stream = ffmpeg.filter(
            stream,
            'drawtext',
            text=text,
            fontfile='/System/Library/Fonts/Supplemental/Arial.ttf',
            fontsize=38,
            fontcolor='white',
            box=1,
            boxcolor='black@0.7',
            boxborderw=5,
            x='(w-text_w)/2',
            y=1000,
            alpha=0.8,
            enable=f'between(t,0,{duration})',
            line_spacing=10
        )
        
        stream = ffmpeg.filter(stream, 'format', 'yuv420p')
        
        # Combine video and audio streams
        stream = ffmpeg.concat(stream, audio, v=1, a=1, n=1)
        
        stream = ffmpeg.output(
            stream,
            output_path,
            acodec='aac',
            ac=2,
            ar='44100',
            vcodec='libx264',
            preset='medium',
            r=30,
            pix_fmt='yuv420p',
            movflags='+faststart',
            strict='-2',
            **{'y': None}
        )
        
        try:
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
        except ffmpeg.Error as e:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', e.stderr.decode('utf8'))
            raise e 