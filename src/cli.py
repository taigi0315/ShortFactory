import os
import json
import uuid
import traceback
from datetime import datetime
from .content_generator import ContentGenerator
from .visual_director import VisualDirector
from .narration_generator import NarrationGenerator
from .video_assembler import VideoAssembler
from .utils.sheets_manager import SheetsManager
from .utils.youtube_manager import YouTubeManager
from config.styles import image_styles

def get_creator_options() -> list[str]:
    """Get available creator options from the prompts directory."""
    prompts_dir = os.path.join("config", "prompts")
    if not os.path.exists(prompts_dir):
        return []
    
    creators = []
    for file in os.listdir(prompts_dir):
        if file.endswith('.yml'):
            creator = os.path.splitext(file)[0]
            creators.append(creator)
    return creators

def get_user_input() -> tuple[str, str]:
    """Get input from the user."""
    print("\n=== Short Factory ===")
    print("Create your Short Video in minutes!")
    
    # Creator selection
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
    
    return creator, detail

class ShortFactoryCLI:
    def __init__(self):
        self.task_id = str(uuid.uuid4())
        self.content_generator = ContentGenerator(self.task_id, "gemini") #gpt-4o, gemini
        self.visual_director = VisualDirector(self.task_id)
        self.narration_generator = NarrationGenerator(self.task_id)
        self.video_assembler = VideoAssembler(self.task_id)
        self.sheets_manager = SheetsManager()
        self.youtube_manager = YouTubeManager()
        
        # Get Google Sheets ID from environment variable
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_ID environment variable is not set.")
    
    def create_short(self):
        """Start YouTube Short creation."""
        try:
            # Get user input
            creator, detail = get_user_input()
            
            print("\nStarting content generation...")
            print(f"Task ID: {self.task_id}")
            
            # 1. Generate content
            content_plan = self.content_generator.generate_content(
                creator,
                detail
            )
            print("\n=== Content Plan ===")
            print(json.dumps(content_plan, indent=2, ensure_ascii=False))

            # 2. Generate visual assets
            visuals = self.visual_director.create_visuals(
                content_plan,
                creator
            )
            print("\n=== Generated Visuals ===")
            print(json.dumps(visuals, indent=2, ensure_ascii=False))

            # 3. Generate audio
            audio = self.narration_generator.generate_narrations(content_plan)
            print("\n=== Generated Audio ===")
            print(json.dumps(audio, indent=2, ensure_ascii=False))

            # 4. Assemble video
            print("\n[4/4] Assembling video")
            print("\nAssembling video...")
            video_path = self.video_assembler.assemble_video(
                content_id=str(uuid.uuid4()),
                content_data=content_plan
            )
            print(f"\n✅ SUCCESS: Video created at {video_path}")
            
            # 5. Upload to YouTube
            print("\n[5/5] Uploading to YouTube")
            try:
                # 다음 업로드 시간 계산
                next_upload_time = self.sheets_manager._calculate_next_upload_time()
                
                # 해시태그 설정
                tags = content_plan.get('hashtags', [])

                # 비디오 제목 설정
                title = content_plan.get('video_title', '')
                if not title:
                    raise ValueError("Video title is not set.")
                
                # 비디오 설명 설정
                description = content_plan.get('video_description', '')
                
                # 공개 설정 (기본값: public)
                privacy_status = 'private'
                
                # 업로드 설정 확인
                print("\nUpload settings:")
                print(f"Title: {title}")
                print(f"Description: {description}")
                print(f"Tags: {' '.join(tags)}")
                print(f"Privacy: {privacy_status}")
                print(f"Scheduled time: {next_upload_time}")
                

                youtube_title = title+' '.join(tags)
                youtube_title = youtube_title[:100] # less than 100 characters
                youtube_description = description+' '.join(tags)
                youtube_description = youtube_description[:5000] # less than 5000 characters


                # YouTube 업로드
                metadata = {
                    'title': youtube_title,
                    'description': youtube_description,
                    'tags': tags,
                    'privacyStatus': privacy_status
                }
                
                response = self.youtube_manager.upload_video(
                    video_path=video_path,
                    metadata=metadata,
                    scheduled_time=next_upload_time
                )
                
                print(f"\n✅ SUCCESS: Video uploaded to YouTube")
                print(f"Video ID: {response.get('id')}")
                print(f"Video URL: https://youtube.com/watch?v={response.get('id')}")
                print(f"Scheduled for: {next_upload_time}")
                
            except Exception as e:
                print(f"\n⚠️ Error uploading to YouTube: {str(e)}")
            
            # Save to Google Sheets after successful video creation
            try:
                # Extract video information from content plan
                video_info = {
                    'video_title': content_plan.get('video_title', ''),
                    'video_description': content_plan.get('video_description', ''),
                    'hashtag': content_plan.get('hashtags', [])
                }
                
                # Convert hashtags list to string if it's a list
                if isinstance(video_info['hashtag'], list):
                    video_info['hashtag'] = ' '.join(video_info['hashtag'])
                
                self.sheets_manager.save_video_info(
                    spreadsheet_id=self.spreadsheet_id,
                    content_plan=video_info,
                    task_id=self.task_id
                )
                print("\n✅ Video information saved to Google Sheets.")
            except Exception as e:
                print(f"\n⚠️ Error saving to Google Sheets: {str(e)}")
            
            return True

        except Exception as e:
            print(f"\n[!] Error occurred: {str(e)}")
            traceback.print_exc()
            return False

def main():
    """Main entry point for the CLI."""
    cli = ShortFactoryCLI()
    cli.create_short()

if __name__ == "__main__":
    main() 