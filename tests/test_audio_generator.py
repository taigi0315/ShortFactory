import pytest
import os
from src.audio_generator import AudioGenerator, AudioType

@pytest.fixture
def audio_generator():
    return AudioGenerator()

@pytest.fixture
def sample_script():
    return """[HOOK]
(효과음: whoosh)
안녕하세요! 오늘은 유튜브 팁에 대해 이야기해볼게요.

[CONTENT]
(효과음: click)
첫 번째로, 이것은 매우 중요한 포인트입니다.
두 번째로, 이것도 꼭 기억해주세요.
마지막으로, 이것이 핵심입니다.

[CONCLUSION]
(효과음: ding)
지금까지 설명한 내용이 도움이 되셨나요?"""

def test_audio_generator_initialization(audio_generator):
    """AudioGenerator 초기화 테스트"""
    assert audio_generator is not None
    assert audio_generator.storage_path == "data/audio.json"
    assert audio_generator.audio_dir == "data/audio"

def test_generate_audio(audio_generator, sample_script):
    """오디오 에셋 생성 테스트"""
    audio_assets = audio_generator.generate_audio(
        script=sample_script,
        topic="유튜브 팁",
        target_audience="교육",
        mood="활기찬"
    )
    
    assert isinstance(audio_assets, list)
    assert len(audio_assets) > 0
    
    # 각 오디오 에셋의 구조 확인
    for asset in audio_assets:
        assert "type" in asset
        assert "content" in asset
        assert "timing" in asset
        assert "duration" in asset
        assert "metadata" in asset

def test_audio_caching(audio_generator, sample_script):
    """오디오 에셋 캐싱 테스트"""
    # 첫 번째 생성
    audio_assets1 = audio_generator.generate_audio(
        script=sample_script,
        topic="유튜브 팁",
        target_audience="교육",
        mood="활기찬"
    )
    
    # 두 번째 생성 (같은 스크립트)
    audio_assets2 = audio_generator.generate_audio(
        script=sample_script,
        topic="유튜브 팁",
        target_audience="교육",
        mood="활기찬"
    )
    
    # 캐시된 결과가 동일한지 확인
    assert audio_assets1 == audio_assets2

def test_different_scripts_generate_different_audio(audio_generator):
    """다른 스크립트에 대해 다른 오디오 에셋이 생성되는지 테스트"""
    script1 = "[HOOK]\n(효과음: whoosh)\n첫 번째 스크립트\n[CONTENT]\n내용\n[CONCLUSION]\n결론"
    script2 = "[HOOK]\n(효과음: whoosh)\n두 번째 스크립트\n[CONTENT]\n다른 내용\n[CONCLUSION]\n다른 결론"
    
    audio_assets1 = audio_generator.generate_audio(
        script=script1,
        topic="테스트",
        target_audience="일반",
        mood="평온한"
    )
    
    audio_assets2 = audio_generator.generate_audio(
        script=script2,
        topic="테스트",
        target_audience="일반",
        mood="평온한"
    )
    
    assert audio_assets1 != audio_assets2

def test_sound_effects_generation(audio_generator, sample_script):
    """효과음 생성 테스트"""
    effects = audio_generator._generate_sound_effects(sample_script)
    
    assert isinstance(effects, list)
    assert len(effects) > 0
    
    # 효과음 타입 확인
    effect_types = [effect["type"] for effect in effects]
    assert all(effect_type == AudioType.SOUND_EFFECT.value for effect_type in effect_types)
    
    # 효과음 마커 확인
    effect_contents = [effect["content"] for effect in effects]
    assert any("whoosh" in content for content in effect_contents)
    assert any("click" in content for content in effect_contents)
    assert any("ding" in content for content in effect_contents)

def test_background_music_generation(audio_generator):
    """배경음악 생성 테스트"""
    background_music = audio_generator._generate_background_music("활기찬")
    
    assert isinstance(background_music, dict)
    assert background_music["type"] == AudioType.BACKGROUND_MUSIC.value
    assert "background_music_활기찬.mp3" in background_music["content"]
    assert background_music["timing"] == 0.0
    assert background_music["duration"] == 60.0
    assert "mood" in background_music["metadata"]
    assert "volume" in background_music["metadata"]

def test_error_handling(audio_generator):
    """오류 처리 테스트"""
    # 잘못된 스크립트 형식으로 테스트
    invalid_script = "잘못된 형식의 스크립트"
    
    audio_assets = audio_generator.generate_audio(
        script=invalid_script,
        topic="테스트",
        target_audience="일반",
        mood="평온한"
    )
    
    # 오류가 발생해도 빈 리스트가 아닌 더미 오디오 에셋이 반환되는지 확인
    assert isinstance(audio_assets, list)
    assert len(audio_assets) > 0
    assert all(asset["metadata"].get("error") for asset in audio_assets)

def test_audio_generator_initialization():
    generator = AudioGenerator()
    assert generator is not None
    assert os.path.exists("data/audio_files")
    assert os.path.exists("data/audio.json")

def test_generate_audio():
    generator = AudioGenerator()
    script = """
[HOOK]
[SOUND:whoosh]
Hey viewers! Ready to explore the fascinating world of octopuses?
[CONTENT]
[SOUND:pop]
1. First up, octopuses are incredibly intelligent creatures!
[SOUND:pop]
2. They can change their color and texture in an instant.
[SOUND:pop]
3. Each tentacle has its own brain!
[CONCLUSION]
[SOUND:ding]
Isn't nature amazing? Don't forget to like and subscribe!
"""
    mood = "peaceful"
    
    audio_assets = generator.generate_audio(script, mood)
    
    assert audio_assets is not None
    assert isinstance(audio_assets, list)
    assert len(audio_assets) > 0
    
    # Check that all three types of audio are present
    audio_types = [asset["type"] for asset in audio_assets]
    assert AudioType.BACKGROUND_MUSIC.value in audio_types
    assert AudioType.SOUND_EFFECT.value in audio_types
    assert AudioType.NARRATION.value in audio_types

def test_background_music_generation():
    generator = AudioGenerator()
    mood = "peaceful"
    
    bg_music = generator._generate_background_music(mood)
    
    assert bg_music["type"] == AudioType.BACKGROUND_MUSIC.value
    assert "content" in bg_music
    assert "timing" in bg_music
    assert "duration" in bg_music
    assert "metadata" in bg_music
    assert bg_music["metadata"]["mood"] == mood
    assert bg_music["metadata"]["volume"] == 0.3

def test_sound_effects_generation():
    generator = AudioGenerator()
    script = """
[HOOK]
[SOUND:whoosh]
Test hook
[CONTENT]
[SOUND:pop]
Test content
[CONCLUSION]
[SOUND:ding]
Test conclusion
"""
    
    effects = generator._generate_sound_effects(script)
    
    assert len(effects) == 3  # One for each section
    for effect in effects:
        assert effect["type"] == AudioType.SOUND_EFFECT.value
        assert "content" in effect
        assert "timing" in effect
        assert "duration" in effect
        assert "metadata" in effect
        assert effect["metadata"]["volume"] == 0.7

def test_narration_generation():
    generator = AudioGenerator()
    script = "Test narration script"
    
    narration = generator._generate_narration(script)
    
    assert narration["type"] == AudioType.NARRATION.value
    assert narration["content"] == script
    assert narration["timing"] == 0.0
    assert "duration" in narration
    assert "file_path" in narration
    assert "metadata" in narration
    assert narration["metadata"]["voice"] == "Josh"
    assert narration["metadata"]["volume"] == 1.0

def test_script_cleaning():
    generator = AudioGenerator()
    script = """
[HOOK]
[SOUND:whoosh]
Test hook
[CONTENT]
[SOUND:pop]
Test content
[CONCLUSION]
[SOUND:ding]
Test conclusion
"""
    
    cleaned = generator._clean_script_for_narration(script)
    
    assert "[HOOK]" not in cleaned
    assert "[CONTENT]" not in cleaned
    assert "[CONCLUSION]" not in cleaned
    assert "[SOUND:" not in cleaned
    assert "Test hook" in cleaned
    assert "Test content" in cleaned
    assert "Test conclusion" in cleaned

def test_audio_caching():
    generator = AudioGenerator()
    script = "Test script"
    mood = "test"
    
    # Generate first audio assets
    audio1 = generator.generate_audio(script, mood)
    
    # Generate second audio assets for the same script
    audio2 = generator.generate_audio(script, mood)
    
    # Check if cached result is returned
    assert audio1 == audio2 