import os
import pytest
from datetime import datetime, timedelta
from src.utils.youtube_manager import YouTubeManager
from src.utils.sheets_manager import SheetsManager

def test_youtube_schedule_system():
    """YouTube 예약 업로드 시스템을 테스트합니다."""
    print("\n=== YouTube 예약 업로드 시스템 테스트 시작 ===\n")
    
    try:
        # 1. 매니저 초기화
        print("1. 매니저 초기화 중...")
        youtube_manager = YouTubeManager()
        sheets_manager = SheetsManager()
        
        # 2. 테스트 비디오 확인
        test_video_path = "data/final_output/b1478f86-eac3-42a2-b788-b6883597eca7_test_content.mp4"
        print(f"\n2. 테스트 비디오 경로: {test_video_path}")
        print(f"   파일 존재 여부: {'있음' if os.path.exists(test_video_path) else '없음'}")
        
        # 3. 예약된 포스트 확인
        print("\n3. 예약된 포스트 확인 및 업데이트 중...")
        updated_posts = sheets_manager.check_and_update_scheduled_posts()
        print(f"   업데이트된 포스트 수: {len(updated_posts)}")
        
        # 4. 다음 사용 가능한 시간 확인
        print("\n4. 다음 사용 가능한 시간 확인 중...")
        next_time = sheets_manager.get_next_available_time()
        print(f"   다음 사용 가능한 시간: {next_time}")
        
        # 5. 비디오 업로드
        print("\n5. 비디오 업로드 시작...")
        metadata = {
            'title': '테스트 비디오',
            'description': '이것은 테스트 비디오입니다.',
            'tags': ['test', 'video']
        }
        
        response = youtube_manager.upload_video(
            video_path=test_video_path,
            metadata=metadata,
            scheduled_time=next_time,
            content_data={'hashtag': 'test video hashtag'}
        )
        
        if 'id' in response:
            print(f"\n✅ 테스트 성공!")
            print(f"비디오 ID: {response['id']}")
            print(f"비디오 URL: https://youtube.com/watch?v={response['id']}")
            print(f"예약 업로드 시간: {next_time}")
            
            # 6. Google Sheets에 정보 저장
            print("\n6. Google Sheets에 정보 저장 중...")
            content_plan = {
                'video_title': metadata['title'],
                'video_description': metadata['description'],
                'hashtag': 'test video hashtag'
            }
            sheets_manager.save_video_info(
                spreadsheet_id=os.getenv('GOOGLE_SHEETS_ID'),
                content_plan=content_plan,
                task_id=response['id']
            )
            print("   정보 저장 완료")
        else:
            raise Exception("비디오 ID를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        raise

if __name__ == "__main__":
    test_youtube_schedule_system() 