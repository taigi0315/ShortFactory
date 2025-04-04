import os
import json
from typing import Dict, List, Optional, Any
import ffmpeg
from PIL import Image
from ...utils.logger import Logger
import platform
import re

class VideoAssembler:
    def __init__(self, task_id: str, creator: str):
        self.task_id = task_id
        self.creator = creator
        self.base_dir = os.path.join("data", creator, task_id)
        self.clips_dir = os.path.join(self.base_dir, "clips")
        self.final_dir = os.path.join("data", creator, "final_output")
        self.images_dir = os.path.join(self.base_dir, "images")
        
        # 디렉토리 생성
        os.makedirs(self.clips_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        self.logger = Logger()
        self._ensure_storage_exists()
        
        # 시스템 폰트 경로 설정
        self.font_path = self._get_system_font_path()
    
    def _ensure_storage_exists(self):
        """로컬 스토리지 디렉토리가 존재하는지 확인합니다."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
    
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
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """텍스트를 문장 단위로 분리합니다."""
        # 문장 끝을 나타내는 구두점들
        sentence_endings = ['.', '!', '?', ';']
        
        sentences = []
        current_sentence = ""
        
        for char in text:
            current_sentence += char
            if char in sentence_endings:
                sentences.append(current_sentence.strip())
                current_sentence = ""
        
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        return sentences

    def _split_long_sentence(self, sentence: str, max_chars: int = 25) -> List[str]:
        """긴 문장을 여러 줄로 분할합니다."""
        # 단어 단위로 분리
        words = sentence.split()
        lines = []
        current_line = ""
        
        for word in words:
            # 현재 줄에 단어를 추가했을 때 최대 길이를 초과하는지 확인
            if len(current_line) + len(word) + 1 <= max_chars:  # +1은 공백을 위한 여유
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word
        
        # 마지막 줄 추가
        if current_line:
            lines.append(current_line.strip())
        
        return lines

    def _create_scene_video(self, scene: Dict[str, Any], scene_index: int, scene_type: str = None) -> str:
        """개별 씬 비디오를 생성합니다."""
        try:
            scene_id = f"{scene_type}_{scene_index}" if scene_type else f"scene_{scene_index}"
            output_path = os.path.join(self.clips_dir, f"{scene_id}.mp4")
            
            # 이미지 경로
            image_name = scene_type if scene_type else f"scene_{scene_index}"
            image_path = os.path.join(self.images_dir, f"{image_name}.png")
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # 오디오 경로
            audio_name = scene_type if scene_type else f"scene_{scene_index}"
            audio_path = os.path.join(self.base_dir, "narrations", f"{audio_name}.mp3")
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio not found: {audio_path}")
            
            # 오디오 길이 측정
            duration = self._get_audio_duration(audio_path)
            
            # 자막 텍스트 준비
            text = scene.get('script', '')
            text = self._escape_special_chars(text)
            
            # 긴 문장을 여러 줄로 나누기 (최대 글자수를 30으로 늘림)
            lines = self._split_long_sentence(text, max_chars=30)
            text = '\n'.join(lines)
            
            # 이미지와 오디오 결합
            stream = (
                ffmpeg
                .input(image_path, loop=1, t=duration)
                .filter('scale', 720, 1280, force_original_aspect_ratio='decrease')
                .filter('pad', 720, 1280, '(ow-iw)/2', '(oh-ih)/2')
                .filter('format', 'yuv420p')
                # 자막 추가
                .filter(
                    'drawtext',
                    text=text,
                    fontfile=self.font_path,
                    fontsize=38,  # 폰트 크기를 더 줄임
                    fontcolor='white',
                    box=1,
                    boxcolor='black@0.7',
                    boxborderw=5,
                    x='(w-text_w)/2',
                    y=800,
                    alpha=0.8,
                    enable=f'between(t,0,{duration})',
                    line_spacing=15  # 줄 간격도 약간 줄임
                )
            )
            
            audio = ffmpeg.input(audio_path)
            
            # 비디오 생성
            stream = (
                ffmpeg
                .output(
                    stream,
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
                    shortest=None
                )
                .overwrite_output()
            )
            
            self.logger.info(f"씬 {scene_id} 비디오 생성 중...")
            stream.run(capture_stdout=True, capture_stderr=True)
            self.logger.info(f"씬 {scene_id} 비디오 생성 완료")
            return output_path
            
        except ffmpeg.Error as e:
            error_msg = f"FFmpeg 에러 (씬 {scene_id}): {e.stderr.decode()}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"비디오 생성 중 예외 발생 (씬 {scene_id}): {str(e)}"
            self.logger.error(error_msg)
            raise
    
    def assemble_video(self, content_id: str, content_data: Dict[str, Any]) -> str:
        """최종 비디오를 조립합니다."""
        try:
            # 1. 각 씬별 비디오 생성
            scene_videos = []
            
            # Hook 처리
            if "hook" in content_data:
                hook_video = self._create_scene_video(content_data["hook"], 0, "hook")
                scene_videos.append(hook_video)
            
            # 메인 씬 처리
            for i, scene in enumerate(content_data["scenes"], 1):
                scene_video = self._create_scene_video(scene, i)
                scene_videos.append(scene_video)
            
            # Conclusion 처리
            if "conclusion" in content_data:
                conclusion_video = self._create_scene_video(content_data["conclusion"], 0, "conclusion")
                scene_videos.append(conclusion_video)
            
            # 2. 씬 목록 파일 생성
            list_file = os.path.join(self.clips_dir, "scenes.txt")
            with open(list_file, "w", encoding='utf-8') as f:
                for video in scene_videos:
                    f.write(f"file '{os.path.abspath(video)}'\n")
            
            # 3. 최종 비디오 생성
            final_output = os.path.join(self.final_dir, f"{self.task_id}_{content_id}.mp4")
            main_video = os.path.join(self.clips_dir, "main_video.mp4")
            
            # 먼저 메인 비디오 생성 (hook + scenes + conclusion)
            stream = (
                ffmpeg
                .input(list_file, format='concat', safe=0)
                .output(
                    main_video,
                    acodec='aac',
                    vcodec='libx264',
                    audio_bitrate='192k',
                    preset='medium',
                    movflags='+faststart',
                    pix_fmt='yuv420p',
                    r=30,
                    ac=2,
                    ar='44100',
                    strict='-2',
                    **{'filter_complex': '[0:v]setpts=PTS/1.1[outv];[0:a]atempo=1.1[outa]',
                       'map': '[outv]',
                       'map:1': '[outa]'}
                )
                .overwrite_output()
            )
            
            self.logger.info("메인 비디오 생성 중...")
            stream.run(capture_stdout=True, capture_stderr=True)
            self.logger.info("메인 비디오 생성 완료")
            
            # 인트로 비디오 경로
            intro_video = os.path.join("assets", "huh_intro.mp4")
            # Update intro video speed 1.2 fast
            fast_intro_video = os.path.join(self.clips_dir, "fast_intro.mp4")
            
            if os.path.exists(intro_video):
                # 인트로 비디오 속도 조정
                stream = (
                    ffmpeg
                    .input(intro_video)
                    .output(
                        fast_intro_video,
                        acodec='aac',
                        vcodec='libx264',
                        audio_bitrate='192k',
                        preset='medium',
                        movflags='+faststart',
                        pix_fmt='yuv420p',
                        r=30,
                        ac=2,
                        ar='44100',
                        strict='-2',
                        **{'filter_complex': '[0:v]setpts=PTS/1.2[v];[0:a]atempo=1.2[a]',
                           'map': '[v]',
                           'map:1': '[a]'}
                    )
                    .overwrite_output()
                )
                
                self.logger.info("인트로 비디오 속도 조정 중...")
                stream.run(capture_stdout=True, capture_stderr=True)
                self.logger.info("인트로 비디오 속도 조정 완료")
                
                # 인트로와 메인 비디오 결합
                final_list_file = os.path.join(self.clips_dir, "final_scenes.txt")
                with open(final_list_file, "w", encoding='utf-8') as f:
                    f.write(f"file '{os.path.abspath(fast_intro_video)}'\n")
                    f.write(f"file '{os.path.abspath(main_video)}'\n")
                
                # 단순 결합 (속도 조정 없이)
                stream = (
                    ffmpeg
                    .input(final_list_file, format='concat', safe=0)
                    .output(
                        final_output,
                        acodec='aac',
                        vcodec='libx264',
                        audio_bitrate='192k',
                        preset='medium',
                        movflags='+faststart',
                        pix_fmt='yuv420p',
                        r=30,
                        ac=2,
                        ar='44100',
                        strict='-2',
                        c='copy'  # 스트림을 그대로 복사
                    )
                    .overwrite_output()
                )
                
                self.logger.info("인트로 추가 중...")
                stream.run(capture_stdout=True, capture_stderr=True)
                self.logger.info("최종 비디오 생성 완료")
                
                # 임시 파일 삭제
                os.remove(final_list_file)
                os.remove(main_video)
                os.remove(fast_intro_video)  # 속도 조정된 인트로 비디오도 삭제
            else:
                # 인트로가 없는 경우 메인 비디오를 최종 출력으로 이동
                os.rename(main_video, final_output)
            
            # 임시 파일 정리
            os.remove(list_file)
            for video in scene_videos:
                os.remove(video)
            
            return final_output
            
        except Exception as e:
            self.logger.error(f"Error assembling video: {str(e)}")
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
            y=800,
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