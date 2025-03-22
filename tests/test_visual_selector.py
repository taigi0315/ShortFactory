import pytest
from src.visual_selector import VisualSelector, VisualSource

def test_visual_selector_initialization():
    selector = VisualSelector()
    assert selector is not None

def test_select_visuals():
    selector = VisualSelector()
    script = """
[HOOK]
Hey viewers! Ready to explore the fascinating world of octopuses?
[CONTENT]
1. First up, octopuses are incredibly intelligent creatures!
2. They can change their color and texture in an instant.
3. Each tentacle has its own brain!
[CONCLUSION]
Isn't nature amazing? Don't forget to like and subscribe!
"""
    
    visuals = selector.select_visuals(script)
    
    assert visuals is not None
    assert isinstance(visuals, list)
    assert len(visuals) > 0
    
    # Check each visual asset structure
    for visual in visuals:
        assert "type" in visual
        assert "content" in visual
        assert "timing" in visual
        assert "style" in visual
        assert "duration" in visual
        assert "source_type" in visual
        assert "source_url" in visual

def test_visual_source_types():
    selector = VisualSelector()
    script = """
[HOOK]
Test hook
[CONTENT]
Test content
[CONCLUSION]
Test conclusion
"""
    
    visuals = selector.select_visuals(script)
    
    # Check that different source types are used
    source_types = [visual["source_type"] for visual in visuals]
    assert VisualSource.AI_VIDEO.value in source_types  # Hook should use video
    assert VisualSource.AI_IMAGE.value in source_types  # Content should use image
    assert VisualSource.WEB_SEARCH.value in source_types  # Conclusion should use web search

def test_visual_storage():
    selector = VisualSelector()
    script = "Test script"
    
    # Generate first visual assets
    visuals1 = selector.select_visuals(script)
    
    # Generate second visual assets for the same script
    visuals2 = selector.select_visuals(script)
    
    # Check if cached result is returned
    assert visuals1 == visuals2 