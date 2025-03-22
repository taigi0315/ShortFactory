import pytest
from src.content_generator import ContentGenerator

def test_content_generator_initialization():
    generator = ContentGenerator()
    assert generator is not None

def test_generate_content_plan():
    generator = ContentGenerator()
    subject = "Interesting facts about Octopuses"
    target_audience = "general"
    tone = "informative"
    duration = 60.0
    
    content_plan = generator.generate_content_plan(subject, target_audience, tone, duration)
    
    assert content_plan is not None
    assert isinstance(content_plan, dict)
    assert "hook" in content_plan
    assert "key_points" in content_plan
    assert "conclusion" in content_plan
    assert "visual_requirements" in content_plan
    assert "music_style" in content_plan

def test_content_plan_storage():
    generator = ContentGenerator()
    subject = "Test subject"
    
    # Generate first content plan
    plan1 = generator.generate_content_plan(subject)
    
    # Generate second content plan for the same subject
    plan2 = generator.generate_content_plan(subject)
    
    # Check if cached result is returned
    assert plan1 == plan2

def test_different_subjects():
    generator = ContentGenerator()
    
    # Generate plan for first subject
    plan1 = generator.generate_content_plan("Naruto")
    
    # Generate plan for second subject
    plan2 = generator.generate_content_plan("Octopuses")
    
    # Check if different plans are generated
    assert plan1 != plan2 