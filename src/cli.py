import os
import json
from typing import Dict, Optional
from .content_generator import ContentGenerator
from .visual_director import VisualDirector
from .audio_generator import AudioGenerator
from .video_assembler import VideoAssembler

def get_user_input() -> tuple[str, str, str, str, int]:
    """Get input from the user."""
    print("\n=== Short Factory ===")
    print("Create your YouTube Short in minutes!")
    
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
    
    # Add number of scenes input
    print("\nEnter the number of scenes (3-10):")
    while True:
        try:
            num_scenes = int(input("Number of scenes: ").strip())
            if 3 <= num_scenes <= 10:
                break
            print("Please enter a number between 3 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    return topic, detail, target_audience, mood, num_scenes

class ProgressTracker:
    def __init__(self):
        self.steps = [
            "Generating content plan",
            "Creating visuals",
            "Generating audio",
            "Assembling video"
        ]
        self.current_step = 0
    
    def update(self, step: str):
        self.current_step += 1
        print(f"\n[{self.current_step}/{len(self.steps)}] {step}")

class ShortFactoryCLI:
    def __init__(self):
        self.content_generator = ContentGenerator()
        self.visual_director = VisualDirector()
        self.audio_generator = AudioGenerator()
        self.video_assembler = VideoAssembler()
        self.progress_tracker = ProgressTracker()
        self._load_config()
    
    def _load_config(self):
        """설정 파일을 로드합니다."""
        config_path = "config/settings.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "output_directory": "data/output",
                "video_settings": {
                    "resolution": "1080x1920",
                    "fps": 30,
                    "background_music_volume": 0.3,
                    "narration_volume": 1.0
                }
            }
    
    def create_short(self):
        """Execute the YouTube Short creation process."""
        try:
            # Get user input
            topic, detail, target_audience, mood, num_scenes = get_user_input()
            
            print("\nStarting content generation...")
            
            # 1. Generate content plan
            self.progress_tracker.update("Generating content plan")
            print("\nGenerating content plan for:")
            print(f"Topic: {topic}")
            print(f"Target Audience: {target_audience}")
            print(f"Mood: {mood}")
            print(f"Number of scenes: {num_scenes}")
            
            content_plan = self.content_generator.generate_content(
                topic,
                detail,
                target_audience,
                mood,
                num_scenes
            )
            print("\n=== Content Plan ===")
            print(json.dumps(content_plan, indent=2))
            
            # 2. Generate visuals
            self.progress_tracker.update("Creating visuals")
            print("\nGenerating visuals for the content plan...")
            visuals = self.visual_director.create_visuals(
                content_plan,
                target_audience,
                mood
            )
            print("\n=== Generated Visuals ===")
            print(json.dumps(visuals, indent=2))
            
            # 3. Generate audio
            self.progress_tracker.update("Generating audio")
            print("\nGenerating audio assets...")
            audio = self.audio_generator.generate_audio_assets(content_plan)
            print("\n=== Generated Audio ===")
            print(json.dumps(audio, indent=2))
            
            # 4. Assemble video
            self.progress_tracker.update("Assembling video")
            print("\nAssembling video...")
            video_path = self.video_assembler.assemble_video(
                content_id=topic,
                content_data=content_plan
            )
            
            if video_path:
                print(f"\n✨ Process completed successfully!")
                print(f"📁 Expected video location: {video_path}")
                
                # Save final metadata
                metadata = {
                    "content_plan": content_plan,
                    "visuals": visuals,
                    "audio": audio,
                    "video_path": video_path
                }
                metadata_path = "data/metadata/latest_generation.json"
                os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2)
                print(f"\n📝 Metadata saved to: {metadata_path}")
            else:
                raise Exception("Failed to complete the process")
            
        except Exception as e:
            print(f"\n[!] 오류 발생: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
        
        return True

    def _generate_video(self, content_id: str) -> str:
        """생성된 콘텐츠를 기반으로 비디오를 생성합니다."""
        try:
            # 콘텐츠 데이터 로드
            content_data = self._load_content_data(content_id)
            if not content_data:
                raise ValueError(f"Content data not found for ID: {content_id}")
            
            # 비디오 어셈블러 초기화
            assembler = VideoAssembler()
            
            # 비디오 생성
            video_path = assembler.assemble_video(
                content_id=content_id,
                content_data=content_data
            )
            
            return video_path
            
        except Exception as e:
            print(f"비디오 생성 중 오류 발생: {str(e)}")
            # 임시 더미 비디오 생성
            dummy_path = "data/output/dummy_video.mp4"
            os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
            return dummy_path

def main():
    """CLI의 메인 진입점입니다."""
    cli = ShortFactoryCLI()
    cli.create_short()

if __name__ == "__main__":
    main() 