import os
import pytest
from src.ai_image_generator import AIImageGenerator

def test_generate_image():
    """Test image generation using Gemini API"""
    # Initialize the generator
    generator = AIImageGenerator()
    
    # Test prompt
    prompt = "Create a beautiful sunset over mountains, digital art style"
    
    # Generate image
    image_path = generator.generate_image(prompt)
    
    # Check if image was created
    assert os.path.exists(image_path), "Image file was not created"
    
    # Check file size
    assert os.path.getsize(image_path) > 0, "Image file is empty"
    
    # Check file extension
    assert image_path.endswith('.png'), "Image file should be PNG format"
    
    # Print metadata
    print(f"\nGenerated Image Metadata:")
    print(f"Prompt: {prompt}")
    print(f"Path: {image_path}")
    print(f"Size: {os.path.getsize(image_path)} bytes")
    print(f"Created: {os.path.getctime(image_path)}") 