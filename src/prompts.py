"""프로젝트에서 사용되는 모든 프롬프트를 관리합니다."""

# 시스템 프롬프트
SYSTEM_PROMPTS = {
    "content_plan": """You are a professional content creator specializing in short-form video content. Your task is to create a complete content plan for a video that can be easily parsed.

Create a content plan for a YouTube Short video about {topic} on {detail}.

Target audience: {target_audience}
Mood: {mood}
Number of scenes: {num_scenes}

FORMAT YOUR RESPONSE USING THE FOLLOWING JSON STRUCTURE:

{{
    "video_title": "Title of the video",
    "video_description": "Brief description of the video content",
    "hook": {{
        "script": "Narration text for the hook",
        "duration_seconds": 4,
        "image_keywords": ["keyword1", "keyword2"],
        "scene_description": "Detailed description of what should be shown in this scene",
        "image_to_video": "Description of how the static image should be animated or transformed into video"
    }},
    "main_points": [
        {{
            "title": "Point 1 title",
            "script": "Narration text for point 1",
            "duration_seconds": 8~15,
            "image_keywords": ["keyword1", "keyword2"],
            "scene_description": "Detailed description of what should be shown in this scene",
            "image_to_video": "Description of how the static image should be animated or transformed into video"
        }},
        {{
            "title": "Point 2 title",
            "script": "Narration text for point 2",
            "duration_seconds": 8~15,
            "image_keywords": ["keyword1", "keyword2"],
            "scene_description": "Detailed description of what should be shown in this scene",
            "image_to_video": "Description of how the static image should be animated or transformed into video"
        }},
        ...
    ],
    "conclusion": {{
        "script": "Narration text for conclusion with call to action",
        "duration_seconds": 5~10,
        "image_keywords": ["keyword1", "keyword2"],
        "scene_description": "Detailed description of what should be shown in this scene",
        "image_to_video": "Description of how the static image should be animated or transformed into video"
    }},
    "overall_style_guide": {{
        "art_style": "Description of overall art style",
        "color_palette": ["color1", "color2", "color3"],
        "mood_elements": ["element1", "element2"],
        "lighting": "Description of lighting style",
        "composition": "Description of composition style"
    }},
    "music_suggestion": "Suggestion for background music that fits the mood",
    "total_duration_seconds": 30
}}

IMPORTANT: Your response must be a valid JSON object. Do not include any text outside the JSON structure.
""",
    
    "visual_director": """
Create a detailed, high-quality image for a YouTube Shorts video scene with the following specifications:

SCENE CONTENT:
"{script}"

IMAGE STYLE REQUIREMENTS:
- Target audience: {target_audience}
- Mood: {mood}
- Visual style: {visual_style}
- Key elements to include: {image_keywords}

TECHNICAL SPECIFICATIONS:
- Aspect ratio: 9:16 (vertical format for mobile viewing)
- High detail and clarity
- Vibrant, attention-grabbing visuals
- Text should be minimal and large if included

COLOR AND COMPOSITION:
- Use a color palette that includes: {color_palette}
- Composition should focus on central elements with clean background
- Lighting should enhance the {mood} atmosphere
- Overall art style: {overall_art_style}

ADDITIONAL NOTES:
This image will be animated with: {image_to_video}
Ensure the composition allows for this animation type.

Generate a single high-quality image that captures this scene perfectly for a YouTube Shorts video.
""",
    
}

# 프롬프트 템플릿 함수
def get_content_plan_prompt(topic: str, detail: str, target_audience: str, mood: str) -> str:
    """콘텐츠 계획 생성을 위한 프롬프트를 반환합니다."""
    return SYSTEM_PROMPTS["content_plan"].format(
        topic=topic,
        detail=detail,
        target_audience=target_audience,
        mood=mood
    )


def get_visual_director_prompt(
    script: str,
    target_audience: str,
    mood: str,
    visual_style: str,
    image_keywords: str,
    color_palette: str,
    image_to_video: str
) -> str:
    """시각적 자산 생성을 위한 프롬프트를 반환합니다.
    
    Args:
        script (str): 장면의 스크립트
        target_audience (str): 대상 청중
        mood (str): 콘텐츠의 분위기
        visual_style (str): 시각적 스타일 (예: 미니멀, 카툰, 3D 등)
        image_keywords (str): 이미지 생성에 사용할 키워드들
        color_palette (str): 사용할 색상 팔레트
        image_to_video (str): 이미지에 적용할 애니메이션 효과
    
    Returns:
        str: 시각적 자산 생성을 위한 프롬프트
    """
    return SYSTEM_PROMPTS["visual_director"].format(
        script=script,
        target_audience=target_audience,
        mood=mood,
        visual_style=visual_style,
        image_keywords=image_keywords,
        color_palette=color_palette,
        image_to_video=image_to_video
    )
