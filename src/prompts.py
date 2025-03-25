"""프로젝트에서 사용되는 모든 프롬프트를 관리합니다."""

# 시스템 프롬프트
SYSTEM_PROMPTS = {
    "content_plan": """You are a professional content creator specializing in short-form video content.
    Your task is to create a complete content plan for a video that can be easily parsed.
    The video should be 60 ~ 180 seconds long.

Create a content plan for a short video about {topic} on {detail}.

Target audience: {target_audience}
Mood: {mood}

FORMAT YOUR RESPONSE USING THE FOLLOWING JSON STRUCTURE:

{{
    "video_title": "Title of the video",
    "video_description": "Brief description of the video content",
    "hook": {{
        "script": "Narration text for the hook, this should be 5~10 seconds long",
        "caption": "script that will be printed over image",
        "image_keywords": ["keyword1", "keyword2"],
        "scene_description": "Provide an extremely detailed visual description of the scene including: primary subjects/objects and their appearance, spatial arrangement, lighting, colors, atmosphere, camera perspective, background elements, textures, and any other important visual details that would allow an AI image generator to create a photorealistic and compelling image. Be specific about what's visible in the foreground, midground, and background.",
        "image_to_video": "Description of how the static image should be animated or transformed into video"
    }},
    "scenes": [
        {{
            "script": "Narration text for scene 1, this should be 15~25 seconds long",
            "caption": "script that will be printed over image",
            "image_keywords": ["keyword1", "keyword2"],
            "scene_description": "Detailed description of what should be shown in this scene",
            "image_to_video": "Description of how the static image should be animated or transformed into video"
        }},
        {{
            "script": "Narration text for scene 2, this should be 15~25 seconds long",
            "caption": "script that will be printed over image",
            "image_keywords": ["keyword1", "keyword2"],
            "scene_description": "Detailed description of what should be shown in this scene",
            "image_to_video": "Description of how the static image should be animated or transformed into video"
        }}
    ],
    "conclusion": {{
        "script": "Narration text for conclusion with call to action, this should be 5~10 seconds long",
        "caption": "script that will be printed over image",
        "image_keywords": ["keyword1", "keyword2"],
        "scene_description": "Detailed description of what should be shown in this scene",
        "image_to_video": "Description of how the static image should be animated or transformed into video"
    }},
    "music_suggestion": "Suggestion for background music that fits the mood"
}}

IMPORTANT SCENE CREATION GUIDELINES:
- Create a natural flow of scenes, with each scene representing a distinct visual moment or story point
- Include an opening hook scene and a conclusion/call-to-action scene
- Each scene should have a clear purpose in advancing the story or explaining the concept
- Hook scene should be 5~10 seconds
- Conclusion scene should be 5~10 seconds
- Other scenes should be 15~25 seconds

SCENE DESCRIPTION GUIDELINES:
- scene_description should include description about main subject, supporting elements, and background elements
- scene_description should include description about positioning of main subject, supporting elements, and background elements
- scene_description should include description about visual balance
- scene_description should include description about space allocation
- scene_description should include description about lighting


IMPORTANT: Your response must be a valid JSON object. Do not include any text outside the JSON structure.
""",
    
    "visual_director": """
Create a detailed, high-quality image for a video scene with the following specifications

SCENE DESCRIPTION: {scene_description}
SCRIPT: {script}
IMAGE STYLE GUIDE: {image_style_guide}

ESSENTIAL VISUAL ELEMENTS:
- Must include: {image_keywords}
- image style guide: {image_style_guide}
- Target audience: {target_audience}
- Mood: {mood}

TECHNICAL SPECIFICATIONS:
- Image ratio must be 9:16 (vertical format for mobile viewing)
- High detail and clarity
- Vibrant, attention-grabbing visuals
- NO WATERMARKS OR LOGOS of any kind (YouTube, TikTok, etc.)

COLOR AND COMPOSITION:
- Lighting should enhance the {mood} atmosphere

ADDITIONAL NOTES:
This image will be animated with: {image_to_video}, Ensure the composition allows for this animation type.

Generate a single high-quality image in 9:16 aspect ratio that captures this scene perfectly for a video.
"""
}

# 프롬프트 템플릿 함수
def get_content_plan_prompt(topic: str, detail: str, target_audience: str, mood: str, image_style: str) -> str:
    """Returns a prompt for content plan generation.
    
    Args:
        topic (str): The main topic of the video
        detail (str): Additional details about the topic
        target_audience (str): The target audience for the video
        mood (str): The desired mood of the video
    
    Returns:
        str: The formatted prompt for content plan generation
    """
    return SYSTEM_PROMPTS["content_plan"].format(
        topic=topic,
        detail=detail,
        target_audience=target_audience,
        mood=mood
    )


def get_visual_director_prompt(
    script: str,
    scene_description: str,
    caption: str,
    target_audience: str,
    mood: str,
    image_keywords: str,
    image_style_guide: str,
    image_to_video: str
) -> str:
    """시각적 자산 생성을 위한 프롬프트를 반환합니다.
    
    Args:
        script (str): 장면의 스크립트
        scene_description (str): 장면의 설명
        target_audience (str): 대상 청중
        mood (str): 콘텐츠의 분위기
        image_keywords (str): 이미지 생성에 사용할 키워드들
        image_style_guide (str): 전체 스타일 가이드
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
        image_style_guide=image_style_guide,
        image_to_video=image_to_video
    )
