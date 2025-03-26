import os
import json
import pytest
from src.content_generator import ContentGenerator
from src.ai_image_generator import AIImageGenerator
from src.audio_generator import AudioGenerator

def test_content_generation_flow():
    """Test the full content generation flow"""
    # Generate content plan
    content_gen = ContentGenerator()
    content_plan = content_gen.generate_content(
        topic="space exploration",
        detail="The future of human space exploration",
        image_style="photorealistic"
    )
    
    # Validate content plan structure
    assert isinstance(content_plan, dict)
    assert "video_title" in content_plan
    assert "video_description" in content_plan
    assert "hook" in content_plan
    assert "scenes" in content_plan
    assert "conclusion" in content_plan
    assert "music_suggestion" in content_plan
    
    # Validate content plan values
    assert len(content_plan["scenes"]) > 0
    assert isinstance(content_plan["hook"]["image_keywords"], list)
    assert isinstance(content_plan["image_style_guide"]["color_palette"], list)

    
    # 3. Generate images for each section
    image_gen = AIImageGenerator()
    image_prompts = [
        "Create a dynamic and engaging image of a rocket launch at night with stars in the background",
        "Show the International Space Station orbiting Earth with astronauts doing a spacewalk",
        "Illustrate Mars exploration with rovers and potential human settlement",
        "Visualize future space tourism with commercial spaceships and space hotels",
        "Create an inspiring image of Earth seen from space with a message about exploration"
    ]
    
    images = []
    for i, prompt in enumerate(image_prompts):
        image_path = image_gen.generate_image(
            prompt=prompt,
            output_path=f"data/images/space_{i+1}.png"
        )
        images.append({
            "prompt": prompt,
            "path": image_path,
            "index": i+1
        })
    
    # 4. Generate narration audio
    audio_gen = AudioGenerator()
    audio_assets = audio_gen.generate_audio_assets(script)
    
    # Save metadata
    metadata = {
        "content_plan": content_plan,
        "script": script,
        "images": images,
        "audio": audio_assets
    }
    
    os.makedirs("data/metadata", exist_ok=True)
    with open("data/metadata/test_generation.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    # Assertions
    assert len(images) == 5, "Should generate 5 images"
    for image in images:
        assert os.path.exists(image["path"]), f"Image {image['path']} should exist"
        assert os.path.getsize(image["path"]) > 0, f"Image {image['path']} should not be empty"
    
    assert "voice" in audio_assets, "Should have voice audio"
    assert os.path.exists(audio_assets["voice"]["path"]), "Voice audio file should exist"
    
    print("\nGeneration Results:")
    print(f"Content Plan: {len(str(content_plan))} characters")
    print(f"Script: {len(str(script))} characters")
    print(f"Images: {len(images)} generated")
    print(f"Audio: {audio_assets['voice']['duration']:.2f} seconds") 