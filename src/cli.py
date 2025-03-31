import os
import json
import uuid
import traceback
from datetime import datetime
from .core.content.content_generator import ContentGenerator
from .core.visual.visual_director import VisualDirector
from .core.audio.narration_generator import NarrationGenerator
from .core.video.video_assembler import VideoAssembler
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

def get_user_input() -> str:
    """사용자 입력을 받습니다."""
    # 사용 가능한 크리에이터 목록 표시
    creators = get_creator_options()
    if not creators:
        raise ValueError("No creator configurations found in config/prompts directory")
    
    print("\n=== Available Creators ===")
    for i, creator in enumerate(creators, 1):
        print(f"{i}. {creator}")
    
    while True:
        try:
            choice = int(input("\nSelect a creator (enter number): "))
            if 1 <= choice <= len(creators):
                creator = creators[choice - 1]
                break
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\nSelected creator: {creator}")
    return creator

class ShortFactoryCLI:
    def __init__(self, creator: str, model: str = "gemini"):
        self.task_id = str(uuid.uuid4())
        self.creator = creator  # 크리에이터 저장
        self.model = model.lower()  # 모델 저장
        self.content_generator = ContentGenerator(self.task_id, model)
        self.visual_director = VisualDirector(self.task_id, creator, model)
        self.narration_generator = NarrationGenerator(self.task_id, creator)
        self.sheets_manager = SheetsManager(creator=creator)
        
        # Get Google Sheets ID from environment variable
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_ID environment variable is not set.")
    
    def create_short(self):
        """Start YouTube Short creation."""
        try:
            # Initialize VideoAssembler with creator
            self.video_assembler = VideoAssembler(self.task_id, self.creator)
            
            # Get next subject from Google Sheets
            next_subject = self.sheets_manager.get_next_subject(self.spreadsheet_id, self.creator)
            if not next_subject:
                print("\nNo pending subjects found in Google Sheets.")
                return False
            
            print(f"\nProcessing subject: {next_subject['subject']}")
            print(f"Created at: {next_subject['creation_time']}")
            print(f"Task ID: {self.task_id}")
            print(f"Row index: {next_subject['row_index']}")
            
            # Initialize YouTube manager with creator
            self.youtube_manager = YouTubeManager(self.creator)
            
            # 1. Generate content
            content_plan = self.content_generator.generate_content(
                self.creator,
                next_subject['subject']
            )
            print("\n=== Content Plan ===")
            print(json.dumps(content_plan, indent=2, ensure_ascii=False))

            # 2. Generate visual assets
            visuals = self.visual_director.create_visuals(
                content_plan,
                self.creator
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
            
            # # 5. Upload to YouTube
            # print("\n[5/5] Uploading to YouTube")
            # try:
            #     # 다음 업로드 시간 계산
            #     next_upload_time = self.sheets_manager.get_next_available_time(self.creator)
                
            #     # 해시태그 설정
            #     tags = content_plan.get('hashtags', [])

            #     # 비디오 제목 설정
            #     title = content_plan.get('video_title', '')
            #     if not title:
            #         raise ValueError("Video title is not set.")
                
            #     # 비디오 설명 설정
            #     description = content_plan.get('video_description', '')
                
            #     # 공개 설정 (기본값: private)
            #     privacy_status = 'private'
                
            #     # 업로드 설정 확인
            #     print("\nUpload settings:")
            #     print(f"Title: {title}")
            #     print(f"Description: {description}")
            #     print(f"Tags: {' '.join(tags)}")
            #     print(f"Privacy: {privacy_status}")
            #     print(f"Scheduled time: {next_upload_time}")
                
            #     youtube_title = title+' '.join(tags)
            #     youtube_title = youtube_title[:100] # less than 100 characters
            #     youtube_description = description+' '.join(tags)
            #     youtube_description = youtube_description[:5000] # less than 5000 characters

            #     # YouTube 업로드
            #     metadata = {
            #         'title': youtube_title,
            #         'description': youtube_description,
            #         'tags': tags,
            #         'privacyStatus': privacy_status
            #     }
                
            #     response = self.youtube_manager.upload_video(
            #         video_path=video_path,
            #         metadata=metadata,
            #         scheduled_time=next_upload_time,
            #         content_data=content_plan
            #     )
                
            #     print(f"\n✅ SUCCESS: Video uploaded to YouTube")
            #     print(f"Video ID: {response.get('id')}")
            #     print(f"Video URL: https://youtube.com/watch?v={response.get('id')}")
            #     print(f"Scheduled for: {next_upload_time}")
                
            #     # 비디오 정보 업데이트
            #     video_id = response.get('id')
            #     video_url = f"https://youtube.com/watch?v={video_id}"
                
            #     # 먼저 비디오 정보를 저장하고 행 번호를 받아옵니다
            #     row_index = self.sheets_manager.save_video_info(
            #         spreadsheet_id=self.spreadsheet_id,
            #         content_plan=content_plan,
            #         task_id=self.task_id,
            #         creator=self.creator,
            #         video_id=video_id,
            #         video_url=video_url,
            #         row_index=next_subject['row_index']
            #     )
                
            #     if row_index:
            #         # 저장된 행 번호를 사용하여 상태 업데이트
            #         self.sheets_manager.update_video_info(
            #             spreadsheet_id=self.spreadsheet_id,
            #             task_id=self.task_id,
            #             creator=self.creator,
            #             updates={
            #                 'video_id': video_id,
            #                 'video_url': video_url,
            #                 'status': 'uploaded'
            #             },
            #             row_index=row_index
            #         )
            #     else:
            #         print("\n⚠️ Warning: Could not update video status in Google Sheets")
            
            # except Exception as e:
            #     print(f"\n⚠️ Error uploading to YouTube: {str(e)}")
            
            # # 6. Save to Google Sheets after successful video creation
            # try:
            #     # Extract video information from content plan
            #     video_info = {
            #         'subject': next_subject['subject'],  # 원본 주제 추가
            #         'video_title': content_plan.get('video_title', ''),
            #         'video_description': content_plan.get('video_description', ''),
            #         'hashtag': content_plan.get('hashtags', [])
            #     }
                
            #     # Convert hashtags list to string if it's a list
            #     if isinstance(video_info['hashtag'], list):
            #         video_info['hashtag'] = ' '.join(video_info['hashtag'])
                
            #     self.sheets_manager.save_video_info(
            #         spreadsheet_id=self.spreadsheet_id,
            #         content_plan=video_info,
            #         task_id=self.task_id,
            #         creator=self.creator,
            #         row_index=next_subject['row_index']
            #     )
            #     print("\n✅ Video information saved to Google Sheets.")
            # except Exception as e:
            #     print(f"\n⚠️ Error saving to Google Sheets: {str(e)}")
            
            # return True

        except Exception as e:
            print(f"\n[!] Error occurred: {str(e)}")
            traceback.print_exc()
            return False

def main():
    """Main entry point for the CLI."""
    print("\n=== Short Factory ===")
    try:
        creator = get_user_input()
        # Initialize CLI with creator
        cli = ShortFactoryCLI(creator=creator)
        cli.create_short()
    except ValueError:
        print("Please enter a valid number.")
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main() 