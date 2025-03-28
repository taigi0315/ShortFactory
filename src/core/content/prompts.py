"""프로젝트에서 사용되는 모든 프롬프트를 관리합니다."""
import os
import yaml


def get_content_plan_prompt(creator: str, detail: str) -> str:
    """Returns a prompt for content plan generation.
    
    Args:
        creator (str): The creator type for the video
        detail (str): Additional details about the content
    
    Returns:
        str: The formatted prompt for content plan generation
    """
    prompt_file = os.path.join("config", "prompts", f"{creator}.yml")
    if os.path.exists(prompt_file):
        with open(prompt_file, 'r', encoding='utf-8') as f:
            try:
                config = yaml.safe_load(f)
                content_prompt = config.get('content_prompt')
                image_style_guide = config.get('image_style_guide')
                
                # Check content_prompt is not empty
                if not content_prompt:
                    raise ValueError(f"Content prompt for {creator} is empty")
                if not image_style_guide:
                    raise ValueError(f"Image style guide for {creator} is empty")
                
                # Get image style guide keys and join them with commas
                image_style_keys = ", ".join(image_style_guide.keys())
                
                # Format content_prompt with all variables at once
                return content_prompt.format(
                    detail=detail,
                    image_style_list=image_style_keys
                )

            except yaml.YAMLError:
                raise ValueError(f"Failed to load creator prompt for {creator}")
    raise ValueError(f"Creator prompt for {creator} not found")


def get_visual_director_prompt(
    script: str,
    scene_description: str,
    image_keywords: str,
    image_style_name: str,
    image_to_video: str,
    creator: str
) -> str:
    """시각적 자산 생성을 위한 프롬프트를 반환합니다.
    
    Args:
        script (str): 장면의 스크립트
        scene_description (str): 장면의 설명
        image_keywords (str): 이미지 생성에 사용할 키워드들
        image_style_name (str): 선택된 이미지 스타일의 이름
        image_to_video (str): 이미지에 적용할 애니메이션 효과
        creator (str): creator 이름
    
    Returns:
        str: 시각적 자산 생성을 위한 프롬프트
    """
    try:
        # creator.yml 파일에서 visual_prompt와 image_style_guide 로드
        prompt_file = os.path.join("config", "prompts", f"{creator}.yml")
        if os.path.exists(prompt_file):
            with open(prompt_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                visual_prompt = config.get('visual_prompt')
                image_style_guide_list = config.get('image_style_guide')
                
                if not visual_prompt:
                    raise ValueError(f"Visual prompt for {creator} is empty")
                if not image_style_guide_list:
                    raise ValueError(f"Image style guide for {creator} is empty")
                
                # Get the description for the selected image style
                if image_style_name not in image_style_guide_list:
                    raise ValueError(f"Image style '{image_style_name}' not found in style guide")
                image_style_guide = image_style_guide_list[image_style_name]
                
                return visual_prompt.format(
                    script=script,
                    scene_description=scene_description,
                    image_keywords=image_keywords,
                    image_style_guide=image_style_guide,
                    image_to_video=image_to_video
                )
        raise ValueError(f"Creator prompt for {creator} not found")
    except yaml.YAMLError:
        raise ValueError(f"Failed to load creator prompt for {creator}")
    except Exception as e:
        raise ValueError(f"Error loading visual prompt: {str(e)}")
