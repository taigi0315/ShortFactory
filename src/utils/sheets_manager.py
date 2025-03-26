"""Utility class for managing Google Sheets"""
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from typing import List, Dict, Any
from datetime import datetime

class SheetsManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = None
        self.service = None
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
    
    def save_video_info(self, spreadsheet_id: str, content_plan: Dict[str, Any]) -> None:
        """Save video information to Google Sheets

        Args:
            spreadsheet_id (str): Google Spreadsheet ID
            content_plan (Dict[str, Any]): Video content information
        """
        try:
            # Prepare data to save
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            values = [
                [
                    now,  # Creation time
                    content_plan.get('video_title', ''),  # Video title
                    content_plan.get('video_description', ''),  # Video description
                    content_plan.get('hashtag', ''),  # Hashtags
                ]
            ]
            
            # Add data
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Sheet1!A:D',  # Add data to columns A-D
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            print(f"{result.get('updates').get('updatedRows')} rows added.")
            
        except Exception as e:
            print(f"Error saving to Google Sheets: {str(e)}")
            raise 