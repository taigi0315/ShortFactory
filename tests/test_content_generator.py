import pytest
from src.content_generator import ContentGenerator

def test_content_generator_initialization():
    generator = ContentGenerator("test_task", "gemini")
    assert generator is not None

def test_generate_content_plan():
    generator = ContentGenerator("test_task", "gemini")
    topic = "Interesting facts about Octopuses"
    detail = "The intelligence and abilities of octopuses"
    image_style = "photorealistic"
    
    content_plan = generator.generate_content(topic, detail, image_style)
    
    assert content_plan is not None
    assert isinstance(content_plan, dict)
    assert "hook" in content_plan
    assert "scenes" in content_plan
    assert "conclusion" in content_plan
    assert "music_suggestion" in content_plan

def test_content_plan_storage():
    generator = ContentGenerator("test_task", "gemini")
    topic = "Test subject"
    detail = "Test detail"
    image_style = "photorealistic"
    
    # Generate first content plan
    plan1 = generator.generate_content(topic, detail, image_style)
    
    # Generate second content plan for the same subject
    plan2 = generator.generate_content(topic, detail, image_style)
    
    # Check if cached result is returned
    assert plan1 == plan2

def test_different_subjects():
    generator = ContentGenerator("test_task", "gemini")
    
    # Generate plan for first subject
    plan1 = generator.generate_content("Naruto", "The story of Naruto", "anime")
    
    # Generate plan for second subject
    plan2 = generator.generate_content("Octopuses", "The intelligence of octopuses", "photorealistic")
    
    # Check if different plans are generated
    assert plan1 != plan2 