import os
from typing import Dict, Optional, Any
from datetime import datetime
import pytz
import yaml
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import pickle

class YouTubeManager:
    def __init__(self, creator: str):
        self.SCOPES = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]
        self.creds = None
        self.youtube = None
        self.creator = creator
        self.channel_id = self._load_channel_id()
        self._setup_credentials()
    
    def _load_channel_id(self) -> str:
        """크리에이터의 YouTube 채널 ID를 로드합니다."""
        try:
            config_path = os.path.join('config', 'prompts', f'{self.creator}.yml')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                channel_id = config.get('youtube_channel_id')
                if not channel_id:
                    raise ValueError(f"Channel ID not found in {config_path}")
                return channel_id
        except Exception as e:
            print(f"채널 ID 로드 중 오류 발생: {str(e)}")
            raise
    
    def _setup_credentials(self):
        """YouTube API 인증을 수행합니다."""
        try:
            # 저장된 토큰이 있는지 확인
            token_file = f'youtube_token_{self.creator}.pickle'
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # 토큰이 없거나 만료된 경우 새로 생성
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        f'credentials_{self.creator}.json',
                        self.SCOPES
                    )
                    self.creds = flow.run_local_server(
                        port=8080,
                        open_browser=True,
                        success_message='인증이 완료되었습니다. 이 창을 닫아주세요.'
                    )
                
                # 토큰 저장
                with open(token_file, 'wb') as token:
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
                    scheduled_time = pytz.timezone('America/Chicago').localize(scheduled_time)
                scheduled_time = scheduled_time.astimezone(utc)
            
            # 비디오 메타데이터 설정
            body = {
                'snippet': {
                    'title': metadata['title'],
                    'description': metadata['description'],
                    'tags': metadata.get('tags', []),
                    'categoryId': '22',  # People & Blogs
                    'channelId': self.channel_id  # 채널 ID 추가
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