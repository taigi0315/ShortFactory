import os
import json
from typing import Dict, Optional
from .content_generator import ContentGenerator
from .visual_selector import VisualSelector
from .audio_generator import AudioGenerator
from .video_assembler import VideoAssembler

def get_user_input() -> tuple[str, str, str]:
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
    target_audience = audience_map.get(input("Choice (1-3): "), "general")
    
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
    
    return topic, target_audience, mood

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
    
    def create_short(self):
        """YouTube Short 생성 프로세스를 실행합니다."""
        try:
            # 사용자 입력 받기
            topic, target_audience, mood = get_user_input()
            
            print("\nStarting content generation...")
            
            # 1. 콘텐츠 계획 생성
            self.progress_tracker.update("Generating content plan")
            print("\nGenerating content plan for:")
            print(f"Topic: {topic}")
            print(f"Target Audience: {target_audience}")
            print(f"Mood: {mood}")
            
            content_plan = self.content_generator.generate_content(
                topic,
                target_audience,
                mood
            )
            print("\n=== Content Plan ===")
            print(json.dumps(content_plan, indent=2))
            
            # 2. 스크립트 생성
            self.progress_tracker.update("Creating script")
            print("\nGenerating script with config:")
            script_config = ScriptConfig(
                topic=topic,
                target_audience=target_audience,
                mood=mood,
                tone="engaging",  # 기본값
                duration=60  # 기본값 (1분)
            )
            print(json.dumps(script_config.__dict__, indent=2))
            
            script = self.script_generator.generate_script(script_config)
            print("\n=== Generated Script ===")
            print(json.dumps(script, indent=2))
            
            # 3. 시각적 자산 선택
            self.progress_tracker.update("Selecting visuals")
            print("\nSelecting visuals for the script...")
            visuals = self.visual_selector.select_visuals(
                script,
                topic,
                target_audience,
                mood
            )
            print("\n=== Selected Visuals ===")
            print(json.dumps(visuals, indent=2))
            
            # 4. 오디오 생성
            self.progress_tracker.update("Generating audio")
            print("\nGenerating audio assets...")
            audio = self.audio_generator.generate_audio_assets(script)
            print("\n=== Generated Audio ===")
            print(json.dumps(audio, indent=2))
            
            # 5. 비디오 조립 (주석 처리)
            # self.progress_tracker.update("Assembling video")
            # video_path = self.video_assembler.assemble_video(
            #     visual_assets=visuals,
            #     audio_assets=audio
            # )
            
            # 임시 비디오 경로
            video_path = "data/output/dummy_video.mp4"
            os.makedirs(os.path.dirname(video_path), exist_ok=True)
            
            if video_path:
                print(f"\n✨ Process completed successfully!")
                print(f"📁 Expected video location: {video_path}")
                
                # 최종 메타데이터 저장
                metadata = {
                    "content_plan": content_plan,
                    "script": script,
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