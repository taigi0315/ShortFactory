import pytest
from src.prompt_generator import PromptGenerator

def test_prompt_generator_initialization():
    generator = PromptGenerator()
    assert generator is not None

def test_generate_image_prompt():
    generator = PromptGenerator()
    story = "A majestic octopus gracefully swimming through a coral reef"
    mood = "peaceful"
    style = "realistic"
    target_audience = "general"
    
    prompt = generator.generate_image_prompt(story, mood, style, target_audience)
    
    assert prompt is not None
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "octopus" in prompt.lower()
    assert "coral reef" in prompt.lower()

def test_generate_video_prompt():
    generator = PromptGenerator()
    story = "A majestic octopus gracefully swimming through a coral reef"
    mood = "peaceful"
    style = "documentary"
    target_audience = "general"
    
    prompt = generator.generate_video_prompt(story, mood, style, target_audience)
    
    assert prompt is not None
    assert isinstance(prompt, str)
    assert len(prompt) > 0
    assert "octopus" in prompt.lower()
    assert "coral reef" in prompt.lower()
    assert any(term in prompt.lower() for term in ["camera", "scene", "transition"])

def test_generate_search_query():
    generator = PromptGenerator()
    story = "A majestic octopus gracefully swimming through a coral reef"
    mood = "peaceful"
    target_audience = "general"
    
    query = generator.generate_search_query(story, mood, target_audience)
    
    assert query is not None
    assert isinstance(query, str)
    assert len(query) > 0
    assert "octopus" in query.lower()
    assert "coral reef" in query.lower()

def test_prompt_caching():
    generator = PromptGenerator()
    story = "Test story"
    mood = "test"
    style = "test"
    target_audience = "test"
    
    # Generate first prompt
    prompt1 = generator.generate_image_prompt(story, mood, style, target_audience)
    
    # Generate second prompt for the same input
    prompt2 = generator.generate_image_prompt(story, mood, style, target_audience)
    
    # Check if cached result is returned
    assert prompt1 == prompt2 