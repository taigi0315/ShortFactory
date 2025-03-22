import pytest
from src.script_generator import ScriptGenerator

def test_script_generator_initialization():
    generator = ScriptGenerator()
    assert generator is not None

def test_generate_script():
    generator = ScriptGenerator()
    game_name = "Gorilla Tag"
    tone = "energetic"
    target_audience = "13-24 year old gamers"
    
    script = generator.generate_script(game_name, tone, target_audience)
    
    assert script is not None
    assert isinstance(script, str)
    assert len(script) > 0
    assert "hook" in script.lower()
    assert "conclusion" in script.lower()

def test_script_structure():
    generator = ScriptGenerator()
    script = generator.generate_script("Test Game", "energetic", "gamers")
    
    # 스크립트 구조 검증
    sections = script.split("\n\n")
    assert len(sections) >= 3  # 최소 3개의 섹션 (hook, content, conclusion)
    
    # 각 섹션의 내용 검증
    assert any("hook" in section.lower() for section in sections)
    assert any("fact" in section.lower() or "feature" in section.lower() for section in sections)
    assert any("conclusion" in section.lower() or "call to action" in section.lower() for section in sections) 