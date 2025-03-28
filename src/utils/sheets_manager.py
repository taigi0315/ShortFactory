"""Utility class for managing Google Sheets"""
import os
import yaml
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from typing import List, Dict, Any, Optional
from datetime import datetime, time, timedelta
from .logger import Logger
import pytz

class SheetsManager:
    def __init__(self):
        self.logger = Logger()
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = None
        self.service = None
        self.spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_ID environment variable is not set.")
        self._setup_credentials()
    
    def _setup_credentials(self):
        """Set up Google Sheets API authentication"""
        # Load token if exists
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        
        # Create new credentials if not valid
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    self.SCOPES
                )
                self.creds = flow.run_local_server(
                    port=8080,
                    open_browser=True,
                    success_message='인증이 완료되었습니다. 이 창을 닫아주세요.'
                )
            
            # Save token
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('sheets', 'v4', credentials=self.creds)
    
    def _get_creator_sheet_name(self, creator: str) -> str:
        """크리에이터의 Google Sheets 시트 이름을 가져옵니다."""
        try:
            config_path = os.path.join('config', 'prompts', f'{creator}.yml')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                sheet_name = config.get('google_sheet_name')
                if not sheet_name:
                    raise ValueError(f"Sheet name not found in {config_path}")
                return sheet_name
        except Exception as e:
            print(f"시트 이름 로드 중 오류 발생: {str(e)}")
            raise

    def save_video_info(self, spreadsheet_id: str, content_plan: Dict[str, Any], task_id: str, creator: str, video_id: str = None, video_url: str = None, row_index: int = None) -> None:
        """Save video information to Google Sheets

        Args:
            spreadsheet_id (str): Google Spreadsheet ID
            content_plan (Dict[str, Any]): Video content information
            task_id (str): Task ID for tracking
            creator (str): Creator name
            video_id (str, optional): YouTube video ID
            video_url (str, optional): YouTube video URL
            row_index (int, optional): Row index to update (1-based index)
        """
        try:
            # 크리에이터의 시트 이름 가져오기
            sheet_name = self._get_creator_sheet_name(creator)
            
            # Prepare data to save
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 다음 업로드 시간 계산
            next_upload_time = self._calculate_next_upload_time(creator)
            
            # 새로운 값 준비
            new_values = [
                content_plan.get('subject', ''),  # Subject (A열)
                now,  # Creation time (B열)
                task_id,  # Task ID (C열)
                content_plan.get('video_title', ''),  # Video title (D열)
                content_plan.get('video_description', ''),  # Video description (E열)
                content_plan.get('hashtag', ''),  # Hashtags (F열)
                "scheduled",  # Upload status (G열)
                next_upload_time.strftime("%Y-%m-%d %H:%M:%S"),  # Scheduled time (H열)
                video_id or "",  # Video ID (I열)
                video_url or "",  # Video URL (J열)
            ]
            
            if row_index:
                # 기존 행 업데이트
                result = self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range=f'{sheet_name}!A{row_index}:J{row_index}',
                    valueInputOption='RAW',
                    body={'values': [new_values]}
                ).execute()
                print(f"Updated row {row_index}")
            else:
                # 새 행 추가
                result = self.service.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_id,
                    range=f'{sheet_name}!A:J',
                    valueInputOption='RAW',
                    insertDataOption='INSERT_ROWS',
                    body={'values': [new_values]}
                ).execute()
                print(f"{result.get('updates').get('updatedRows')} rows added.")
            
        except Exception as e:
            print(f"Error saving to Google Sheets: {str(e)}")
            raise

    def get_next_subject(self, spreadsheet_id: str, creator: str) -> Optional[Dict[str, Any]]:
        """처리되지 않은 가장 오래된 주제를 가져옵니다.

        Args:
            spreadsheet_id (str): Google Spreadsheet ID
            creator (str): Creator name

        Returns:
            Optional[Dict[str, Any]]: 다음 주제 정보 또는 None
                - subject: 주제
                - row_index: 행 번호
                - creation_time: 생성 시간
        """
        try:
            sheet_name = self._get_creator_sheet_name(creator)
            
            # 현재 시트의 모든 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A:J'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print('No data found.')
                return None
            
            # 처리되지 않은 주제들을 생성 시간순으로 정렬
            unprocessed_subjects = []
            for i, row in enumerate(values):
                # 첫 번째 열(Subject)만 있으면 됨
                if len(row) >= 1:
                    subject = row[0]  # A열: Subject
                    if not subject:  # 주제가 비어있으면 스킵
                        continue
                        
                    # Video ID 확인 (I열)
                    video_id = row[8] if len(row) > 8 else ""
                    if video_id:  # 이미 처리된 주제는 스킵
                        continue
                    
                    # Creation time 확인 (B열)
                    creation_time = row[1] if len(row) > 1 else None
                    if creation_time:
                        try:
                            creation_datetime = datetime.strptime(creation_time, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            # 유효하지 않은 날짜면 현재 시간 사용
                            creation_datetime = datetime.now()
                    else:
                        # creation_time이 없으면 현재 시간 사용
                        creation_datetime = datetime.now()
                    
                    unprocessed_subjects.append({
                        'subject': subject,
                        'row_index': i + 1,  # 1-based index
                        'creation_time': creation_datetime
                    })
            
            if not unprocessed_subjects:
                print('No pending subjects found.')
                return None
            
            # 생성 시간순으로 정렬 (가장 오래된 것부터)
            unprocessed_subjects.sort(key=lambda x: x['creation_time'])
            
            # 가장 오래된 주제 반환
            return unprocessed_subjects[0]
            
        except Exception as e:
            print(f"Error getting next subject: {str(e)}")
            raise

    def update_video_info(self, spreadsheet_id: str, task_id: str, creator: str, updates: Dict[str, Any], row_index: int = None) -> None:
        """비디오 정보를 업데이트합니다.

        Args:
            spreadsheet_id (str): Google Spreadsheet ID
            task_id (str): Task ID
            creator (str): Creator name
            updates (Dict[str, Any]): 업데이트할 정보
            row_index (int, optional): 업데이트할 행 번호 (1-based index)
        """
        try:
            sheet_name = self._get_creator_sheet_name(creator)
            
            # 행 번호가 주어지지 않은 경우, task_id로 행을 찾음
            if row_index is None:
                result = self.service.spreadsheets().values().get(
                    spreadsheetId=spreadsheet_id,
                    range=f'{sheet_name}!A:J'
                ).execute()
                
                values = result.get('values', [])
                for i, row in enumerate(values):
                    if len(row) > 2 and row[2] == task_id:  # C열: Task ID
                        row_index = i + 1  # 1-based index
                        break
            
            if not row_index:
                raise ValueError(f"Row not found for task_id: {task_id}")
            
            # 현재 행의 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A{row_index}:J{row_index}'
            ).execute()
            
            current_values = result.get('values', [[]])[0]
            # 현재 값이 10개보다 적으면 10개가 되도록 빈 문자열 추가
            while len(current_values) < 10:
                current_values.append("")
            
            # 업데이트할 값 준비
            new_values = current_values.copy()
            
            # 업데이트 매핑
            column_mapping = {
                'video_title': 3,      # D열
                'video_description': 4, # E열
                'hashtag': 5,          # F열
                'status': 6,           # G열
                'scheduled_time': 7,   # H열
                'video_id': 8,         # I열
                'video_url': 9         # J열
            }
            
            # 값 업데이트
            for key, value in updates.items():
                if key in column_mapping:
                    new_values[column_mapping[key]] = value
            
            # 업데이트 실행
            body = {
                'values': [new_values]
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A{row_index}:J{row_index}',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Updated {result.get('updatedCells')} cells.")
            
        except Exception as e:
            print(f"Error updating video information: {str(e)}")
            raise
    
    def _calculate_next_upload_time(self, creator: str) -> datetime:
        """다음 업로드 시간을 계산합니다."""
        try:
            # 현재 시간 가져오기 (UTC)
            now = datetime.now(pytz.UTC)
            
            # 기본적으로 다음 날 오전 9시 (미국 중부 시간)
            central = pytz.timezone('America/Chicago')
            next_time = (now + timedelta(days=1)).astimezone(central)
            next_time = next_time.replace(
                hour=9, 
                minute=0, 
                second=0, 
                microsecond=0
            )
            
            return next_time
            
        except Exception as e:
            print(f"Error calculating next upload time: {str(e)}")
            raise
    
    def update_upload_status(self, spreadsheet_id: str, task_id: str, status: str) -> None:
        """업로드 상태를 업데이트합니다."""
        try:
            # 현재 시트의 모든 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range='science_fact!A:G'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print('No data found.')
                return
            
            # task_id로 행 찾기
            for i, row in enumerate(values):
                if row[1] == task_id:  # task_id는 B열(인덱스 1)
                    # 상태 업데이트
                    values[i][6] = status  # G열(인덱스 6)에 상태 저장
                    
                    # 상태가 'posted'인 경우 예약 시간을 현재 시간으로 업데이트
                    if status == "posted":
                        values[i][5] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # F열(인덱스 5)에 현재 시간 저장
                    break
            
            # 업데이트된 데이터 저장
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='science_fact!A:G',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"Status updated to '{status}' for task {task_id}")
            
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            raise
    
    def check_and_update_scheduled_posts(self, creator: str) -> List[Dict[str, Any]]:
        """예약된 포스트를 확인하고 업데이트합니다."""
        try:
            sheet_name = self._get_creator_sheet_name(creator)
            # 구현 필요
            return []
        except Exception as e:
            print(f"Error checking scheduled posts: {str(e)}")
            raise

    def get_next_available_time(self, creator: str) -> datetime:
        """다음 사용 가능한 시간을 찾습니다."""
        try:
            # 현재 시트의 모든 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='science_fact!A:G'
            ).execute()
            
            values = result.get('values', [])
            scheduled_times = []
            
            # 예약된 시간 수집
            if values:
                for row in values[1:]:  # 헤더 제외
                    if len(row) > 5:  # F열에 날짜가 있는 경우
                        try:
                            scheduled_time = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")
                            scheduled_times.append(scheduled_time)
                        except (ValueError, IndexError):
                            continue
            
            # 현재 시간
            now = datetime.now()
            
            # 업로드 시간 목록 (10:00, 18:00, 22:00)
            upload_times = [
                time(8, 0),  # 8:00 AM
                time(13, 0),  # 1:00 PM
                time(19, 0),  # 7:00 PM
            ]
            
            # 다음 7일 동안의 가능한 시간 확인
            for days_ahead in range(7):
                target_date = now.date() + timedelta(days=days_ahead)
                
                for upload_time in upload_times:
                    target_datetime = datetime.combine(target_date, upload_time)
                    
                    # 현재 시간보다 이전이면 건너뛰기
                    if target_datetime <= now:
                        continue
                    
                    # 이미 예약된 시간과 비교
                    is_available = True
                    for scheduled_time in scheduled_times:
                        if abs((target_datetime - scheduled_time).total_seconds()) < 3600:  # 1시간 간격
                            is_available = False
                            break
                    
                    if is_available:
                        return target_datetime
            
            raise ValueError("No available upload slots found in the next 7 days")
            
        except Exception as e:
            print(f"Error finding next available time: {str(e)}")
            raise

    def update_video_statistics(self, spreadsheet_id: str, creator: str) -> None:
        """모든 비디오의 통계 정보를 업데이트합니다.

        Args:
            spreadsheet_id (str): Google Spreadsheet ID
            creator (str): Creator name
        """
        try:
            sheet_name = self._get_creator_sheet_name(creator)
            
            # 현재 시트의 모든 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=f'{sheet_name}!A:M'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                print('No data found.')
                return
            
            # YouTube 매니저 초기화
            from .youtube_manager import YouTubeManager
            youtube_manager = YouTubeManager(creator)
            
            # 각 행의 비디오 정보 업데이트
            for i, row in enumerate(values):
                if len(row) < 8:  # 최소 8열(H열)이 있어야 함
                    continue
                    
                video_id = row[7]  # H열: Video ID
                if not video_id:  # 비디오 ID가 없는 경우 스킵
                    continue
                
                try:
                    # 비디오 통계 정보 가져오기
                    stats = youtube_manager.get_video_statistics(video_id)
                    
                    # 업데이트할 정보
                    updates = {
                        'views': stats['views'],
                        'likes': stats['likes'],
                        'comments': stats['comments'],
                        'status': stats['status']
                    }
                    
                    # 성능 메모 추가 (예: 조회수/좋아요 비율)
                    try:
                        views = int(stats['views'])
                        likes = int(stats['likes'])
                        if views > 0:
                            engagement_rate = (likes / views) * 100
                            updates['performance_notes'] = f"Engagement rate: {engagement_rate:.2f}%"
                    except (ValueError, ZeroDivisionError):
                        updates['performance_notes'] = "Engagement rate: N/A"
                    
                    # 행 업데이트
                    if 'views' in updates:
                        row[9] = updates['views']  # J열
                    if 'likes' in updates:
                        row[10] = updates['likes']  # K열
                    if 'comments' in updates:
                        row[11] = updates['comments']  # L열
                    if 'performance_notes' in updates:
                        row[12] = updates['performance_notes']  # M열
                    
                    # 업데이트된 데이터 저장
                    body = {
                        'values': [row]
                    }
                    
                    result = self.service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'{sheet_name}!A{i+1}:M{i+1}',
                        valueInputOption='RAW',
                        body=body
                    ).execute()
                    
                    print(f"Updated statistics for video {video_id}")
                    
                except Exception as e:
                    print(f"Error updating statistics for video {video_id}: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"Error updating video statistics: {str(e)}")
            raise 