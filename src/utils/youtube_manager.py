import os
from typing import Dict, Optional, Any
from datetime import datetime
import pytz
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import pickle

class YouTubeManager:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]
        self.creds = None
        self.youtube = None
        self._setup_credentials()
    
    def _setup_credentials(self):
        """YouTube API 인증을 수행합니다."""
        try:
            # 저장된 토큰이 있는지 확인
            if os.path.exists('youtube_token.pickle'):
                with open('youtube_token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)
            
            # 토큰이 없거나 만료된 경우 새로 생성
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
                
                # 토큰 저장
                with open('youtube_token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # YouTube API 서비스 생성
            self.youtube = build('youtube', 'v3', credentials=self.creds)
            
        except Exception as e:
            print(f"인증 중 오류 발생: {str(e)}")
            raise
    
    def upload_video(self, video_path: str, metadata: Dict[str, Any], scheduled_time: Optional[datetime] = None, content_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload video to YouTube with metadata"""
        try:
            # 해시태그 처리
            if content_data and 'hashtag' in content_data:
                hashtags = content_data['hashtag'].split()
                hashtag_string = ' '.join(f'#{tag}' for tag in hashtags)
                metadata['title'] = f"{metadata['title']} {hashtag_string}"
                metadata['description'] = f"{metadata['description']}\n\n{hashtag_string}"
            
            # Title must be 100 characters or less
            if len(metadata['title']) > 100:
                metadata['title'] = metadata['title'][:100]
            
            # 예약 시간을 UTC로 변환
            if scheduled_time:
                utc = pytz.UTC
                if scheduled_time.tzinfo is None:
                    scheduled_time = pytz.timezone('Asia/Seoul').localize(scheduled_time)
                scheduled_time = scheduled_time.astimezone(utc)
            
            # 비디오 메타데이터 설정
            body = {
                'snippet': {
                    'title': metadata['title'],
                    'description': metadata['description'],
                    'tags': metadata.get('tags', []),
                    'categoryId': '22'  # People & Blogs
                },
                'status': {
                    'privacyStatus': 'private',  # 예약을 위해 private으로 설정
                    'publishAt': scheduled_time.isoformat() if scheduled_time else None
                }
            }
            
            # 업로드 요청
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(
                    video_path,
                    chunksize=-1,
                    resumable=True
                )
            )
            
            # 업로드 실행
            response = request.execute()
            
            return response
            
        except Exception as e:
            print(f"Error uploading video: {str(e)}")
            raise 