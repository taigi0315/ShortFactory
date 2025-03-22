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
        "caption": "script that will be printed over image",
        "duration_seconds": 4,
        "image_keywords": ["keyword1", "keyword2"],
        "scene_description": "Detailed description of what should be shown in this scene",
        "image_to_video": "Description of how the static image should be animated or transformed into video"
    }},
    "scenes": [
        {{
            "scene_number": 1,
            "script": "Narration text for scene 1",
            "caption": "script that will be printed over image",
            "duration_seconds": 8~15,
            "image_keywords": ["keyword1", "keyword2"],
            "scene_description": "Detailed description of what should be shown in this scene",
            "image_to_video": "Description of how the static image should be animated or transformed into video"
        }},
        {{
            "scene_number": 2,
            "script": "Narration text for scene 2",
            "caption": "script that will be printed over image",
            "duration_seconds": 8~15,
            "image_keywords": ["keyword1", "keyword2"],
            "scene_description": "Detailed description of what should be shown in this scene",
            "image_to_video": "Description of how the static image should be animated or transformed into video"
        }},
        ... (generate exactly {num_scenes} scenes)
    ],
    "conclusion": {{
        "script": "Narration text for conclusion with call to action",
        "caption": "script that will be printed over image",
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
}}

IMPORTANT: Your response must be a valid JSON object. Do not include any text outside the JSON structure.
Make sure to generate exactly {num_scenes} scenes in the "scenes" array.
""",
    
    "visual_director": """
Create a detailed, high-quality image for a YouTube Shorts video scene with the following specifications:

SCENE DESCRIPTION: {scene_description}
SCRIPT: {script}

IMAGE STYLE REQUIREMENTS:
- Overall art style: {overall_style_guide}
- Target audience: {target_audience}
- Mood: {mood}
- Key elements to include: {image_keywords}

TECHNICAL SPECIFICATIONS:
- Aspect ratio: 9:16 (vertical format for mobile viewing)
- High detail and clarity
- Vibrant, attention-grabbing visuals
- Text should be minimal and large if included

COLOR AND COMPOSITION:
- Composition should focus on central elements with clean background
- Lighting should enhance the {mood} atmosphere
- Overall art style: {overall_style_guide}

ADDITIONAL NOTES:
This image will be animated with: {image_to_video}
Ensure the composition allows for this animation type.

Generate a single high-quality image that captures this scene perfectly for a YouTube Shorts video.
""",
    
}

# 프롬프트 템플릿 함수
def get_content_plan_prompt(topic: str, detail: str, target_audience: str, mood: str, num_scenes: int) -> str:
    """Returns a prompt for content plan generation.
    
    Args:
        topic (str): The main topic of the video
        detail (str): Additional details about the topic
        target_audience (str): The target audience for the video
        mood (str): The desired mood of the video
        num_scenes (int): Number of scenes to generate (3-10)
    
    Returns:
        str: The formatted prompt for content plan generation
    """
    return SYSTEM_PROMPTS["content_plan"].format(
        topic=topic,
        detail=detail,
        target_audience=target_audience,
        mood=mood,
        num_scenes=num_scenes
    )


def get_visual_director_prompt(
    script: str,
    scene_description: str,
    caption: str,
    target_audience: str,
    mood: str,
    image_keywords: str,
    overall_style_guide: str,
    image_to_video: str
) -> str:
    """시각적 자산 생성을 위한 프롬프트를 반환합니다.
    
    Args:
        script (str): 장면의 스크립트
        scene_description (str): 장면의 설명
        target_audience (str): 대상 청중
        mood (str): 콘텐츠의 분위기
        image_keywords (str): 이미지 생성에 사용할 키워드들
        overall_style_guide (str): 전체 스타일 가이드
        image_to_video (str): 이미지에 적용할 애니메이션 효과
    
    Returns:
        str: 시각적 자산 생성을 위한 프롬프트
    """
    return SYSTEM_PROMPTS["visual_director"].format(
        script=script,
        scene_description=scene_description,
        caption=caption,
        target_audience=target_audience,
        mood=mood,
        image_keywords=image_keywords,
        overall_style_guide=overall_style_guide,
        image_to_video=image_to_video
    )
