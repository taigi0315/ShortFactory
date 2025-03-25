import ffmpeg
from typing import Optional, Tuple
from ..utils.logger import Logger

class AudioProcessor:
    def __init__(self):
        self.logger = Logger()
    
    def get_audio_duration(self, file_path: str) -> float:
        """오디오 파일의 길이를 초 단위로 반환합니다."""
        try:
            probe = ffmpeg.probe(file_path)
            audio_info = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
            return float(probe['format']['duration'])
        except Exception as e:
            self.logger.error(f"오디오 길이 확인 실패: {e}")
            return 0.0
    
    def adjust_audio_duration(self, input_path: str, output_path: str, target_duration: float) -> None:
        """오디오 파일의 길이를 조정합니다."""
        try:
            current_duration = self.get_audio_duration(input_path)
            if current_duration == 0:
                raise ValueError("오디오 파일 길이를 확인할 수 없습니다.")
            
            # 오디오 속도 조정
            speed_factor = current_duration / target_duration
            
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.filter(stream, 'atempo', speed_factor)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True)
            
            self.logger.info(f"오디오 길이 조정 완료: {target_duration}초")
        except Exception as e:
            self.logger.error(f"오디오 길이 조정 실패: {e}")
            raise
    
    def merge_audio_files(self, files: list, output_path: str) -> None:
        """여러 오디오 파일을 하나로 병합합니다."""
        try:
            # 임시 파일 생성
            temp_files = []
            for i, file in enumerate(files):
                temp_file = f"{output_path}.temp{i}.wav"
                stream = ffmpeg.input(file)
                stream = ffmpeg.output(stream, temp_file, acodec='pcm_s16le')
                ffmpeg.run(stream, overwrite_output=True)
                temp_files.append(temp_file)
            
            # 파일 목록 생성
            with open('temp_list.txt', 'w') as f:
                for temp_file in temp_files:
                    f.write(f"file '{temp_file}'\n")
            
            # 파일 병합
            stream = ffmpeg.input('temp_list.txt', format='concat', safe=0)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True)
            
            # 임시 파일 정리
            for temp_file in temp_files:
                import os
                os.remove(temp_file)
            os.remove('temp_list.txt')
            
            self.logger.info("오디오 파일 병합 완료")
        except Exception as e:
            self.logger.error(f"오디오 파일 병합 실패: {e}")
            raise 