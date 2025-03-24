import os
import json
import uuid
import traceback
from .content_generator import ContentGenerator
from .visual_director import VisualDirector
from .narration_generator import NarrationGenerator
from .video_assembler import VideoAssembler
from config.styles import image_styles

def get_user_input() -> tuple[str, str, str, str, str, int]:
    """사용자로부터 입력을 받습니다."""
    print("\n=== Short Factory ===")
    print("Create your Short Video in minutes!")
    
    topic = input("\nEnter the topic for your short: ")
    detail = input("Enter the detail for your short: ")

    print("\nSelect target audience:")
    print("1. General")
    print("2. Educational")
    print("3. Entertainment")
    print("4. Professional")
    print("5. Children")
    print("6. Teenagers")
    print("7. Seniors")
    audience_map = {
        "1": "general",
        "2": "educational",
        "3": "entertainment",
        "4": "professional",
        "5": "children",
        "6": "teenagers",
        "7": "seniors"
    }
    target_audience = audience_map.get(input("Choice (1-7): "), "general")
    
    print("\nSelect mood:")
    print("1. Energetic")
    print("2. Peaceful")
    print("3. Funny")
    print("4. Inspirational")
    print("5. Dramatic")
    print("6. Mysterious")
    print("7. Romantic")
    print("8. Professional")
    print("9. Playful")
    mood_map = {
        "1": "energetic",
        "2": "peaceful",
        "3": "funny",
        "4": "inspirational",
        "5": "dramatic",
        "6": "mysterious",
        "7": "romantic",
        "8": "professional",
        "9": "playful"
    }
    mood = mood_map.get(input("Choice (1-9): "), "energetic")

    print("\nSelect image style:")
    style_options = list(image_styles.keys())
    for i, style_name in enumerate(style_options, 1):
        print(f"{i}. {style_name}: {image_styles[style_name]}")
    
    while True:
        try:
            choice = int(input("\nChoice (1-{}): ".format(len(style_options))))
            if 1 <= choice <= len(style_options):
                image_style = style_options[choice - 1]
                break
            print(f"Please enter a number between 1 and {len(style_options)}.")
        except ValueError:
            print("Please enter a valid number.")
    
    return topic, detail, target_audience, mood, image_style

class ShortFactoryCLI:
    def __init__(self):
        self.task_id = str(uuid.uuid4())
        self.content_generator = ContentGenerator(self.task_id, "gemini") #gpt-4o, gemini
        self.visual_director = VisualDirector(self.task_id)
        self.narration_generator = NarrationGenerator(self.task_id)
        self.video_assembler = VideoAssembler(self.task_id)
    
    def create_short(self):
        """YouTube Short 생성을 시작합니다."""
        try:
            # 사용자 입력 받기
            topic, detail, target_audience, mood, image_style = get_user_input()
            
            print("\nStarting content generation...")
            print(f"Task ID: {self.task_id}")
            
            # 1. 콘텐츠 생성
            content_plan = self.content_generator.generate_content(
                topic,
                detail,
                target_audience,
                mood,
                image_style
            )
            print("\n=== Content Plan ===")
            print(json.dumps(content_plan, indent=2, ensure_ascii=False))

            # 2. 시각적 에셋 생성
            visuals = self.visual_director.create_visuals(
                content_plan,
                target_audience,
                mood,
                image_style
            )
            print("\n=== Generated Visuals ===")
            print(json.dumps(visuals, indent=2, ensure_ascii=False))

            # 3. 오디오 생성
            audio = self.narration_generator.generate_narrations(content_plan)
            print("\n=== Generated Audio ===")
            print(json.dumps(audio, indent=2, ensure_ascii=False))

            # 4. 비디오 조립
            print("\n[4/4] Assembling video")
            print("\nAssembling video...")
            video_path = self.video_assembler.assemble_video(
                content_id=str(uuid.uuid4()),
                content_data=content_plan
            )
            print(f"\n✅ SUCCESS: Video created at {video_path}")
            
            return True

        except Exception as e:
            print(f"\n[!] 오류 발생: {str(e)}")
            traceback.print_exc()
            return False

def main():
    """CLI의 메인 진입점입니다."""
    cli = ShortFactoryCLI()
    cli.create_short()

if __name__ == "__main__":
    main() 