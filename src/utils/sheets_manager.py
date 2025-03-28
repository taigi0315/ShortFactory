"""Utility class for managing Google Sheets"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from typing import List, Dict, Any, Optional
from datetime import datetime, time, timedelta
from .logger import Logger

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
    
    def save_video_info(self, spreadsheet_id: str, content_plan: Dict[str, Any], task_id: str) -> None:
        """Save video information to Google Sheets

        Args:
            spreadsheet_id (str): Google Spreadsheet ID
            content_plan (Dict[str, Any]): Video content information
            task_id (str): Task ID for tracking
        """
        try:
            # Prepare data to save
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 다음 업로드 시간 계산
            next_upload_time = self._calculate_next_upload_time()
            
            values = [
                [
                    now,  # Creation time
                    task_id,  # Task ID
                    content_plan.get('video_title', ''),  # Video title
                    content_plan.get('video_description', ''),  # Video description
                    content_plan.get('hashtag', ''),  # Hashtags
                    "scheduled",  # Upload status - 초기 상태를 'scheduled'로 설정
                    next_upload_time.strftime("%Y-%m-%d %H:%M:%S"),  # Next upload time
                    
                ]
            ]
            
            # Add data
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='science_fact!A:G',  # Add data to columns A-G
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"{result.get('updates').get('updatedRows')} rows added.")
            
        except Exception as e:
            print(f"Error saving to Google Sheets: {str(e)}")
            raise
    
    def _calculate_next_upload_time(self) -> datetime:
        """다음 업로드 시간을 계산합니다."""
        now = datetime.now()
        current_time = now.time()
        
        # 업로드 시간 목록 (10:00, 18:00, 22:00)
        upload_times = [
            time(10, 0),  # 10:00 AM
            time(14, 0),  # 2:00 PM
            time(18, 0),  # 6:00 PM
            time(22, 0)   # 10:00 PM
        ]
        
        # 현재 시트의 모든 데이터 가져오기
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range='science_fact!A:G'
        ).execute()
        
        values = result.get('values', [])
        if not values:
            # 데이터가 없는 경우 현재 시간 이후의 다음 시간대 선택
            next_time = None
            for upload_time in upload_times:
                if current_time < upload_time:
                    next_time = upload_time
                    break
            
            if next_time is None:
                next_time = upload_times[0]
                now = now.replace(day=now.day + 1)
            
            return now.replace(
                hour=next_time.hour,
                minute=next_time.minute,
                second=0,
                microsecond=0
            )
        
        # 이미 예약된 시간대 확인
        scheduled_times = []
        for row in values:
            if len(row) >= 7:  # G열(인덱스 6)까지 있는지 확인
                try:
                    status = row[5]  # F열: status
                    if status == "scheduled":  # scheduled 상태인 경우만 확인
                        scheduled_time = datetime.strptime(row[6], "%Y-%m-%d %H:%M:%S")  # G열: scheduled_time
                        scheduled_times.append(scheduled_time)
                except (ValueError, IndexError):
                    continue
        
        # 현재 시간부터 7일 동안의 가능한 시간대 찾기
        for days_ahead in range(7):  # 최대 7일까지 확인
            target_date = now.replace(day=now.day + days_ahead)
            
            for upload_time in upload_times:
                target_datetime = target_date.replace(
                    hour=upload_time.hour,
                    minute=upload_time.minute,
                    second=0,
                    microsecond=0
                )
                
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
        
        # 7일 내에 가능한 시간대를 찾지 못한 경우
        raise ValueError("No available upload slots found in the next 7 days")
    
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
    
    def check_and_update_scheduled_posts(self) -> List[Dict[str, Any]]:
        """예약된 포스트를 확인하고 업데이트합니다."""
        try:
            # 현재 시트의 모든 데이터 가져오기
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range='science_fact!A:G'
            ).execute()
            
            values = result.get('values', [])
            if not values:
                return []
            
            # 헤더 제거
            headers = values[0]
            rows = values[1:]
            
            # 현재 시간
            now = datetime.now()
            posts_to_update = []
            
            for i, row in enumerate(rows, start=2):  # start=2는 헤더 다음 행부터 시작
                try:
                    if len(row) < 7:  # 필요한 모든 컬럼이 없는 경우 스킵
                        continue
                        
                    # 필요한 데이터 추출
                    task_id = row[1]  # B열: task_id
                    status = row[6]  # G열: status
                    
                    # 이미 'posted' 상태인 경우 스킵
                    if status == "posted":
                        continue
                        
                    try:
                        scheduled_time = datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S")  # F열: scheduled_time
                    except ValueError:
                        print(f"Warning: Invalid date format in row {i}, skipping...")
                        continue
                    
                    # 예약 시간이 지났고 상태가 'scheduled'인 경우
                    if scheduled_time < now and status == "scheduled":
                        # 상태를 'posted'로 업데이트
                        self.update_upload_status(self.spreadsheet_id, task_id, "posted")
                        posts_to_update.append({
                            "task_id": task_id,
                            "scheduled_time": scheduled_time,
                            "row_index": i
                        })
                except (ValueError, IndexError) as e:
                    print(f"Warning: Error processing row {i}: {str(e)}")
                    continue
            
            return posts_to_update
            
        except Exception as e:
            print(f"Error checking scheduled posts: {str(e)}")
            raise

    def get_next_available_time(self) -> datetime:
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
                time(10, 0),  # 10:00 AM
                time(14, 0),  # 02:00 AM
                time(17, 0),  # 5:00 PM
                time(22, 0)   # 10:00 PM
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