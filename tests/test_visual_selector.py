import pytest
from src.visual_selector import VisualSelector, VisualSource

@pytest.fixture
def visual_selector():
    return VisualSelector()

@pytest.fixture
def sample_script():
    return """[HOOK]
이 영상에서 여러분에게 특별한 팁을 공유할게요!

[CONTENT]
첫 번째, 이것은 매우 중요한 포인트입니다.
두 번째, 이것도 꼭 기억해주세요.
마지막으로, 이것이 핵심입니다.

[CONCLUSION]
지금까지 설명한 내용이 도움이 되셨나요?"""

def test_visual_selector_initialization(visual_selector):
    """VisualSelector 초기화 테스트"""
    assert visual_selector is not None
    assert visual_selector.storage_path == "data/visuals.json"
    assert visual_selector.visual_dir == "data/visuals"

def test_select_visuals(visual_selector, sample_script):
    """시각적 에셋 선택 테스트"""
    visuals = visual_selector.select_visuals(
        script=sample_script,
        topic="유튜브 팁",
        target_audience="교육",
        mood="활기찬"
    )
    
    assert isinstance(visuals, list)
    assert len(visuals) > 0
    
    # 각 시각적 에셋의 구조 확인
    for visual in visuals:
        assert "type" in visual
        assert "content" in visual
        assert "timing" in visual
        assert "duration" in visual
        assert "source_type" in visual
        assert "metadata" in visual

def test_visual_caching(visual_selector, sample_script):
    """시각적 에셋 캐싱 테스트"""
    # 첫 번째 생성
    visuals1 = visual_selector.select_visuals(
        script=sample_script,
        topic="유튜브 팁",
        target_audience="교육",
        mood="활기찬"
    )
    
    # 두 번째 생성 (같은 스크립트)
    visuals2 = visual_selector.select_visuals(
        script=sample_script,
        topic="유튜브 팁",
        target_audience="교육",
        mood="활기찬"
    )
    
    # 캐시된 결과가 동일한지 확인
    assert visuals1 == visuals2

def test_different_scripts_generate_different_visuals(visual_selector):
    """다른 스크립트에 대해 다른 시각적 에셋이 생성되는지 테스트"""
    script1 = "[HOOK]\n첫 번째 스크립트\n[CONTENT]\n내용\n[CONCLUSION]\n결론"
    script2 = "[HOOK]\n두 번째 스크립트\n[CONTENT]\n다른 내용\n[CONCLUSION]\n다른 결론"
    
    visuals1 = visual_selector.select_visuals(
        script=script1,
        topic="테스트",
        target_audience="일반",
        mood="평온한"
    )
    
    visuals2 = visual_selector.select_visuals(
        script=script2,
        topic="테스트",
        target_audience="일반",
        mood="평온한"
    )
    
    assert visuals1 != visuals2

def test_visual_source_types(visual_selector):
    """시각적 소스 타입 결정 테스트"""
    # 훅 섹션
    hook_source = visual_selector._determine_visual_type("hook")
    assert hook_source == VisualSource.AI_VIDEO
    
    # 콘텐츠 섹션
    content_source = visual_selector._determine_visual_type("content")
    assert content_source == VisualSource.AI_IMAGE
    
    # 결론 섹션
    conclusion_source = visual_selector._determine_visual_type("conclusion")
    assert conclusion_source == VisualSource.WEB_SEARCH

def test_error_handling(visual_selector):
    """오류 처리 테스트"""
    # 잘못된 스크립트 형식으로 테스트
    invalid_script = "잘못된 형식의 스크립트"
    
    visuals = visual_selector.select_visuals(
        script=invalid_script,
        topic="테스트",
        target_audience="일반",
        mood="평온한"
    )
    
    # 오류가 발생해도 빈 리스트가 아닌 더미 시각적 에셋이 반환되는지 확인
    assert isinstance(visuals, list)
    assert len(visuals) > 0
    assert all(visual["metadata"].get("error") == "Failed to generate visual" 
              for visual in visuals) 