import os
import json
import uuid
import traceback
from .content_generator import ContentGenerator
from .visual_director import VisualDirector
from .narration_generator import NarrationGenerator
from .video_assembler import VideoAssembler
from config.styles import image_styles

def get_creator_options() -> list[str]:
    """프롬프트 디렉토리에서 사용 가능한 creator 옵션들을 가져옵니다."""
    prompts_dir = os.path.join("config", "prompts")
    if not os.path.exists(prompts_dir):
        return []
    
    creators = []
    for file in os.listdir(prompts_dir):
        if file.endswith('.yml'):
            creator = os.path.splitext(file)[0]
            creators.append(creator)
    return creators

def get_user_input() -> tuple[str, str, str]:
    """사용자로부터 입력을 받습니다."""
    print("\n=== Short Factory ===")
    print("Create your Short Video in minutes!")
    
    # Creator 선택
    creators = get_creator_options()
    if creators:
        print("\nSelect creator type:")
        for i, creator in enumerate(creators, 1):
            print(f"{i}. {creator}")
        
        while True:
            try:
                choice = int(input("\nChoice (1-{}): ".format(len(creators))))
                if 1 <= choice <= len(creators):
                    creator = creators[choice - 1]
                    break
                print(f"Please enter a number between 1 and {len(creators)}.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        creator = input("\nEnter creator type (or press Enter to skip): ").strip()
    
    detail = input("Enter the detail for your short: ")

    # print("\nSelect image style:")
    # style_options = list(image_styles.keys())
    # for i, style_name in enumerate(style_options, 1):
    #     print(f"{i}. {style_name}: {image_styles[style_name]}")
    
    # while True:
    #     try:
    #         choice = int(input("\nChoice (1-{}): ".format(len(style_options))))
    #         if 1 <= choice <= len(style_options):
    #             image_style = style_options[choice - 1]
    #             break
    #         print(f"Please enter a number between 1 and {len(style_options)}.")
    #     except ValueError:
    #         print("Please enter a valid number.")
    
    return creator, detail

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
            creator, detail = get_user_input()
            
            print("\nStarting content generation...")
            print(f"Task ID: {self.task_id}")
            
            # 1. 콘텐츠 생성
            content_plan = self.content_generator.generate_content(
                creator,
                detail
            )
            print("\n=== Content Plan ===")
            print(json.dumps(content_plan, indent=2, ensure_ascii=False))

            # 2. 시각적 에셋 생성
            visuals = self.visual_director.create_visuals(
                content_plan,
                creator
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