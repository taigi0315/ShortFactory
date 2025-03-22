import pytest
import os
import numpy as np
from PIL import Image
from src.video_assembler import VideoAssembler

@pytest.fixture
def video_assembler():
    return VideoAssembler()

@pytest.fixture
def test_data_dir(tmp_path):
    """테스트용 데이터 디렉토리를 생성합니다."""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    
    # 테스트용 이미지 생성
    image = Image.fromarray(np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8))
    image_path = data_dir / "test_image.jpg"
    image.save(image_path)
    
    # 테스트용 비디오 생성 (5초 길이의 검은 화면)
    video_path = data_dir / "test_video.mp4"
    os.system(f"ffmpeg -f lavfi -i color=c=black:s=1920x1080:d=5 -c:v libx264 {video_path}")
    
    # 테스트용 오디오 생성 (10초 길이의 무음)
    audio_path = data_dir / "test_audio.mp3"
    os.system(f"ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -q:a 9 -acodec libmp3lame {audio_path}")
    
    return data_dir

@pytest.fixture
def sample_visual_assets(test_data_dir):
    return [
        {
            "type": "image",
            "content": str(test_data_dir / "test_image.jpg"),
            "timing": 0.0,
            "duration": 5.0,
            "source_type": "AI_IMAGE",
            "metadata": {
                "prompt": "테스트 이미지 1",
                "style": "현대적"
            }
        },
        {
            "type": "video",
            "content": str(test_data_dir / "test_video.mp4"),
            "timing": 5.0,
            "duration": 5.0,
            "source_type": "AI_VIDEO",
            "metadata": {
                "prompt": "테스트 비디오",
                "style": "동적"
            }
        },
        {
            "type": "image",
            "content": str(test_data_dir / "test_image.jpg"),
            "timing": 10.0,
            "duration": 5.0,
            "source_type": "AI_IMAGE",
            "metadata": {
                "prompt": "테스트 이미지 2",
                "style": "현대적"
            }
        }
    ]

@pytest.fixture
def sample_audio_assets(test_data_dir):
    return [
        {
            "type": "NARRATION",
            "content": str(test_data_dir / "test_audio.mp3"),
            "timing": 0.0,
            "duration": 15.0,  # 전체 나레이션 길이
            "metadata": {
                "voice_id": "voice_1",
                "volume": 1.0
            }
        },
        {
            "type": "SOUND_EFFECT",
            "content": str(test_data_dir / "test_audio.mp3"),
            "timing": 5.0,  # 비디오 시작 시점에 효과음
            "duration": 1.0,
            "metadata": {
                "effect_type": "whoosh",
                "volume": 0.5
            }
        }
    ]

def test_video_assembler_initialization(video_assembler):
    """VideoAssembler 초기화 테스트"""
    assert video_assembler is not None
    assert video_assembler.output_dir == "data/output"
    assert os.path.exists(video_assembler.output_dir)

def test_create_video_clips(video_assembler, sample_visual_assets):
    """비디오 클립 생성 테스트"""
    clips = video_assembler._create_video_clips(sample_visual_assets)
    
    assert isinstance(clips, list)
    assert len(clips) == len(sample_visual_assets)
    
    # 각 클립의 속성 확인
    for clip in clips:
        assert hasattr(clip, 'duration')
        assert hasattr(clip, 'start')
        assert hasattr(clip, 'end')

def test_create_audio_tracks(video_assembler, sample_audio_assets):
    """오디오 트랙 생성 테스트"""
    tracks = video_assembler._create_audio_tracks(sample_audio_assets)
    
    assert isinstance(tracks, list)
    assert len(tracks) == len(sample_audio_assets)
    
    # 각 트랙의 속성 확인
    for track in tracks:
        assert hasattr(track, 'duration')
        assert hasattr(track, 'start')
        assert hasattr(track, 'end')

def test_combine_video_and_audio(video_assembler, sample_visual_assets, sample_audio_assets):
    """비디오와 오디오 결합 테스트"""
    video_clips = video_assembler._create_video_clips(sample_visual_assets)
    audio_tracks = video_assembler._create_audio_tracks(sample_audio_assets)
    
    final_video = video_assembler._combine_video_and_audio(video_clips, audio_tracks)
    
    assert final_video is not None
    assert hasattr(final_video, 'duration')
    assert hasattr(final_video, 'audio')

def test_save_final_video(video_assembler, sample_visual_assets, sample_audio_assets):
    """최종 비디오 저장 테스트"""
    video_clips = video_assembler._create_video_clips(sample_visual_assets)
    audio_tracks = video_assembler._create_audio_tracks(sample_audio_assets)
    final_video = video_assembler._combine_video_and_audio(video_clips, audio_tracks)
    
    output_path = video_assembler._save_final_video(final_video)
    
    assert isinstance(output_path, str)
    assert output_path.startswith(video_assembler.output_dir)
    assert output_path.endswith('.mp4')
    assert os.path.exists(output_path)

def test_assemble_video(video_assembler, sample_visual_assets, sample_audio_assets):
    """전체 비디오 어셈블리 프로세스 테스트"""
    script = "[HOOK]\n테스트 스크립트\n[CONTENT]\n내용\n[CONCLUSION]\n결론"
    
    output_path = video_assembler.assemble_video(
        script=script,
        visual_assets=sample_visual_assets,
        audio_assets=sample_audio_assets
    )
    
    assert isinstance(output_path, str)
    assert output_path.startswith(video_assembler.output_dir)
    assert output_path.endswith('.mp4')
    assert os.path.exists(output_path)

def test_error_handling(video_assembler):
    """오류 처리 테스트"""
    # 존재하지 않는 파일로 테스트
    invalid_assets = [{
        "type": "image",
        "content": "nonexistent_file.jpg",
        "timing": 0.0,
        "duration": 5.0
    }]
    
    with pytest.raises(Exception):
        video_assembler.assemble_video(
            script="테스트",
            visual_assets=invalid_assets,
            audio_assets=[]
        ) 