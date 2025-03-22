import os
import json
from typing import Dict, Optional
from .content_generator import ContentGenerator
from .script_generator import ScriptGenerator, ScriptConfig
from .visual_selector import VisualSelector
from .audio_generator import AudioGenerator
from .video_assembler import VideoAssembler

class ProgressTracker:
    def __init__(self):
        self.steps = [
            "Generating content plan",
            "Creating script",
            "Selecting visuals",
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
        self.script_generator = ScriptGenerator()
        self.visual_selector = VisualSelector()
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
    
    def _get_user_input(self) -> Dict:
        """사용자로부터 입력을 받습니다."""
        print("\n=== Short Factory ===")
        print("Create your YouTube Short in minutes!")
        
        topic = input("\nEnter the topic for your short: ")
        
        print("\nSelect target audience:")
        print("1. General")
        print("2. Educational")
        print("3. Entertainment")
        audience_map = {
            "1": "general",
            "2": "educational",
            "3": "entertainment"
        }
        audience = audience_map.get(input("Choice (1-3): "), "general")
        
        print("\nSelect mood:")
        print("1. Energetic")
        print("2. Peaceful")
        print("3. Funny")
        mood_map = {
            "1": "energetic",
            "2": "peaceful",
            "3": "funny"
        }
        mood = mood_map.get(input("Choice (1-3): "), "energetic")
        
        return {
            "topic": topic,
            "audience": audience,
            "mood": mood
        }
    
    def create_short(self):
        """YouTube Short 생성 프로세스를 실행합니다."""
        try:
            # 사용자 입력 받기
            user_input = self._get_user_input()
            
            print("\nStarting content generation...")
            
            # 1. 콘텐츠 계획 생성
            self.progress_tracker.update("Generating content plan")
            content_plan = self.content_generator.generate_content(
                user_input["topic"],
                user_input["audience"],
                user_input["mood"]
            )
            
            # 2. 스크립트 생성
            self.progress_tracker.update("Creating script")
            script_config = ScriptConfig(
                topic=user_input["topic"],
                target_audience=user_input["audience"],
                mood=user_input["mood"],
                tone="engaging",  # 기본값
                duration=60  # 기본값 (1분)
            )
            script = self.script_generator.generate_script(script_config)
            
            # 3. 시각적 자산 선택
            self.progress_tracker.update("Selecting visuals")
            visuals = self.visual_selector.select_visuals(
                script,
                user_input["topic"],
                user_input["audience"],
                user_input["mood"]
            )
            
            # 4. 오디오 생성
            self.progress_tracker.update("Generating audio")
            audio = self.audio_generator.generate_audio(
                script,
                user_input["topic"],
                user_input["audience"],
                user_input["mood"]
            )
            
            # 5. 비디오 조립
            self.progress_tracker.update("Assembling video")
            video_path = self.video_assembler.assemble_video(
                visual_assets=visuals,
                audio_assets=audio
            )
            
            if video_path and os.path.exists(video_path):
                print(f"\n✨ Video created successfully!")
                print(f"📁 Location: {video_path}")
            else:
                raise Exception("Failed to create video file")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please check your configuration and try again.")
            return False
        
        return True

def main():
    """CLI의 메인 진입점입니다."""
    cli = ShortFactoryCLI()
    cli.create_short()

if __name__ == "__main__":
    main() 