import pytest
import os
from src.audio_generator import AudioGenerator, AudioType

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