"""프로젝트에서 사용되는 모든 프롬프트를 관리합니다."""

# 시스템 프롬프트
SYSTEM_PROMPTS = {
    "content_creator": "You are a professional content creator specializing in short-form video content.",
    "script_writer": "You are an expert script writer for short-form video content.",
    "visual_director": "You are a visual director specializing in creating engaging short-form video content.",
    "audio_engineer": "You are an audio engineer specializing in creating engaging soundscapes for short-form video content."
}

# 콘텐츠 생성 프롬프트
CONTENT_PROMPTS = {
    "content_plan": """You are a professional content creator specializing in short-form video content. Your task is to create a complete content plan for a video that can be easily parsed.

Create a content plan for a YouTube Short video about {topic}.

Target audience: {target_audience}
Mood: {mood}

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
        {{
            "title": "Point 3 title",
            "script": "Narration text for point 3",
            "duration_seconds": 8~15,
            "image_keywords": ["keyword1", "keyword2"],
            "scene_description": "Detailed description of what should be shown in this scene",
            "image_to_video": "Description of how the static image should be animated or transformed into video"
        }}
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
    
    "visual_selection": """
Select appropriate visuals for a YouTube Short video based on the following script:

Script:
{script}

Target audience: {target_audience}
Mood: {mood}

Please provide:
1. Visual descriptions for each scene
2. Suggested transitions
3. Visual effects recommendations
4. Color scheme suggestions

Make it visually engaging and suitable for short-form video content.
""",
    
    "audio_planning": """
Create an audio plan for a YouTube Short video based on the following script:

Script:
{script}

Target audience: {target_audience}
Mood: {mood}

Please provide:
1. Background music suggestions
2. Sound effects recommendations
3. Voice-over style guidelines
4. Audio mixing recommendations

Make it sonically engaging and suitable for short-form video content.
"""
}

# 프롬프트 템플릿 함수
def get_content_plan_prompt(topic: str, target_audience: str, mood: str) -> str:
    """콘텐츠 계획 생성을 위한 프롬프트를 반환합니다."""
    return CONTENT_PROMPTS["content_plan"].format(
        topic=topic,
        target_audience=target_audience,
        mood=mood
    )

def get_script_prompt(content_plan: str, target_audience: str, mood: str, tone: str, duration: int) -> str:
    """스크립트 생성을 위한 프롬프트를 반환합니다."""
    return CONTENT_PROMPTS["script"].format(
        content_plan=content_plan,
        target_audience=target_audience,
        mood=mood,
        tone=tone,
        duration=duration
    )

def get_visual_selection_prompt(script: str, target_audience: str, mood: str) -> str:
    """시각적 자산 선택을 위한 프롬프트를 반환합니다."""
    return CONTENT_PROMPTS["visual_selection"].format(
        script=script,
        target_audience=target_audience,
        mood=mood
    )

def get_audio_planning_prompt(script: str, target_audience: str, mood: str) -> str:
    """오디오 계획 생성을 위한 프롬프트를 반환합니다."""
    return CONTENT_PROMPTS["audio_planning"].format(
        script=script,
        target_audience=target_audience,
        mood=mood
    ) 