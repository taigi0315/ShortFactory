import pytest
from src.script_generator import ScriptGenerator, ScriptConfig

@pytest.fixture
def script_generator():
    return ScriptGenerator()

@pytest.fixture
def script_config():
    return ScriptConfig(
        topic="유튜브 팁",
        target_audience="교육",
        mood="활기찬",
        tone="전문적",
        duration=60
    )

def test_script_generator_initialization(script_generator):
    """ScriptGenerator 초기화 테스트"""
    assert script_generator is not None
    assert script_generator.storage_path == "data/scripts.json"

def test_generate_script(script_generator, script_config):
    """스크립트 생성 테스트"""
    script = script_generator.generate_script(script_config)
    
    assert isinstance(script, str)
    assert len(script) > 0
    
    # 스크립트 구조 확인
    assert "[HOOK]" in script
    assert "[CONTENT]" in script
    assert "[CONCLUSION]" in script
    
    # 효과음 마커 확인
    assert "(효과음: whoosh)" in script
    assert "(효과음: click)" in script
    assert "(효과음: ding)" in script

def test_script_caching(script_generator, script_config):
    """스크립트 캐싱 테스트"""
    # 첫 번째 생성
    script1 = script_generator.generate_script(script_config)
    
    # 두 번째 생성 (같은 설정)
    script2 = script_generator.generate_script(script_config)
    
    # 캐시된 결과가 동일한지 확인
    assert script1 == script2

def test_different_configs_generate_different_scripts(script_generator):
    """다른 설정에 대해 다른 스크립트가 생성되는지 테스트"""
    config1 = ScriptConfig(
        topic="첫 번째 주제",
        target_audience="교육",
        mood="활기찬",
        tone="전문적",
        duration=60
    )
    
    config2 = ScriptConfig(
        topic="두 번째 주제",
        target_audience="교육",
        mood="활기찬",
        tone="전문적",
        duration=60
    )
    
    script1 = script_generator.generate_script(config1)
    script2 = script_generator.generate_script(config2)
    
    assert script1 != script2

def test_error_handling(script_generator):
    """오류 처리 테스트"""
    # 잘못된 설정으로 테스트
    invalid_config = ScriptConfig(
        topic="",  # 빈 주제
        target_audience="",
        mood="",
        tone="",
        duration=0
    )
    
    script = script_generator.generate_script(invalid_config)
    
    # 오류가 발생해도 더미 스크립트가 반환되는지 확인
    assert isinstance(script, str)
    assert len(script) > 0
    assert "[HOOK]" in script
    assert "[CONTENT]" in script
    assert "[CONCLUSION]" in script

def test_script_key_generation(script_generator, script_config):
    """스크립트 키 생성 테스트"""
    key = script_generator._generate_script_key(script_config)
    
    assert isinstance(key, str)
    assert len(key) > 0
    assert script_config.topic in key
    assert script_config.target_audience in key
    assert script_config.mood in key
    assert script_config.tone in key
    assert str(script_config.duration) in key 