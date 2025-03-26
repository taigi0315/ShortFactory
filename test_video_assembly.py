import os
from PIL import Image
import numpy as np
from src.video_assembler import VideoAssembler
import json
import pytest

def create_dummy_image(width: int, height: int, color: tuple) -> Image.Image:
    """테스트용 더미 이미지를 생성합니다."""
    return Image.fromarray(np.full((height, width, 3), color, dtype=np.uint8))

def create_dummy_audio(duration: int, output_path: str):
    """테스트용 더미 오디오 파일을 생성합니다."""
    import wave
    import struct
    
    # 임시 WAV 파일 생성
    temp_wav = output_path.replace('.mp3', '.wav')
    
    # 오디오 설정
    sample_rate = 44100
    num_channels = 2  # 스테레오
    sample_width = 2
    
    # WAV 파일 생성
    with wave.open(temp_wav, 'w') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        
        # 무음 데이터 생성 (스테레오)
        num_frames = int(duration * sample_rate)
        for _ in range(num_frames):
            wav_file.writeframes(struct.pack('hh', 0, 0))
    
    # WAV를 MP3로 변환
    os.system(f'ffmpeg -i {temp_wav} -codec:a libmp3lame -qscale:a 2 {output_path}')
    
    # 임시 WAV 파일 삭제
    os.remove(temp_wav)

def setup_test_files(task_id: str):
    """테스트에 필요한 디렉토리와 파일들을 생성합니다."""
    # 프로젝트 루트 디렉토리 찾기
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 디렉토리 생성
    base_dir = os.path.join(project_root, "data", task_id)
    dirs = [
        os.path.join(base_dir, "images"),
        os.path.join(base_dir, "narration"),
        os.path.join(base_dir, "output", "clips"),
        os.path.join(base_dir, "output", "final")
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # 테스트 소스 디렉토리에서 파일 복사
    source_dir = os.path.join(project_root, "data", "test_source")
    
    # 이미지 파일 복사
    for img_file in os.listdir(os.path.join(source_dir, "images")):
        if img_file.endswith(".png"):
            src_path = os.path.join(source_dir, "images", img_file)
            dst_path = os.path.join(base_dir, "images", img_file)
            if not os.path.exists(dst_path):
                os.system(f"cp {src_path} {dst_path}")
    
    # 나레이션 파일 복사
    for audio_file in os.listdir(os.path.join(source_dir, "narration")):
        if audio_file.endswith(".mp3"):
            src_path = os.path.join(source_dir, "narration", audio_file)
            dst_path = os.path.join(base_dir, "narration", audio_file)
            if not os.path.exists(dst_path):
                os.system(f"cp {src_path} {dst_path}")

def test_video_assembly():
    task_id = "7e5edd1f-f61c-4e36-9d84-62846e44699e"
    content_id = "test_video"
    
    # 테스트 파일 생성
    setup_test_files(task_id)
    
    # 테스트용 콘텐츠 데이터 생성
    content_data = {
        "hook": {
            "script": "Welcome to our video!",
            "caption": "Introduction",
            "image_keywords": ["hook"],
            "scene_description": "Opening scene",
            "image_to_video": "fade in"
        },
        "scenes": [
            {
                "script": "First scene content",
                "caption": "Scene 1",
                "image_keywords": ["scene1"],
                "scene_description": "First main scene",
                "image_to_video": "zoom in"
            },
            {
                "script": "Second scene content",
                "caption": "Scene 2",
                "image_keywords": ["scene2"],
                "scene_description": "Second main scene",
                "image_to_video": "pan left"
            },
            {
                "script": "Third scene content",
                "caption": "Scene 3",
                "image_keywords": ["scene3"],
                "scene_description": "Third main scene",
                "image_to_video": "zoom out"
            }
        ],
        "conclusion": {
            "script": "Thank you for watching!",
            "caption": "Conclusion",
            "image_keywords": ["conclusion"],
            "scene_description": "Closing scene",
            "image_to_video": "fade out"
        }
    }
    
    # 비디오 조립 실행
    assembler = VideoAssembler(task_id)
    output_path = assembler.assemble_video(content_id, content_data)
    print(f"비디오가 생성되었습니다: {output_path}")

def test_video_assembly_with_korean():
    """한글 자막이 포함된 비디오 생성 테스트"""
    # 기존 실행의 task_id 사용
    task_id = "928d6209-5b01-495c-9b97-660e6ffd462e"
    
    # VideoAssembler 인스턴스 생성
    assembler = VideoAssembler(task_id)
    
    # content_plan.json 파일 로드
    content_plan_path = os.path.join("data", task_id, "prompts", "content_plan_response.txt")
    with open(content_plan_path, 'r', encoding='utf-8') as f:
        content_plan = json.loads(f.read())
    
    # 비디오 생성
    try:
        output_path = assembler.assemble_video(
            content_id="korean_test",
            content_data=content_plan
        )
        
        # 결과 검증
        assert os.path.exists(output_path), f"비디오 파일이 생성되지 않았습니다: {output_path}"
        assert os.path.getsize(output_path) > 0, "비디오 파일이 비어있습니다"
        
        print(f"\n✅ 테스트 성공: 비디오가 생성되었습니다.")
        print(f"📁 비디오 경로: {output_path}")
        
    except Exception as e:
        pytest.fail(f"비디오 생성 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_video_assembly_with_korean() 