import os
import pytest
from src.utils.sheets_manager import SheetsManager

def test_sheets_manager():
    """Test Google Sheets integration with sample data"""
    
    # Sample content plan
    content_plan = {
        "video_title": "Test Video Title",
        "video_description": "This is a test video description",
        "hashtag": "#test #shortfactory #automation"
    }
    
    # Initialize SheetsManager
    sheets_manager = SheetsManager()
    
    # Get spreadsheet ID from environment
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_ID')
    if not spreadsheet_id:
        pytest.skip("GOOGLE_SHEETS_ID environment variable not set")
    
    try:
        # Try saving to Google Sheets
        sheets_manager.save_video_info(
            spreadsheet_id=spreadsheet_id,
            content_plan=content_plan
        )
        print("\n✅ Test successful: Data saved to Google Sheets")
        
    except Exception as e:
        pytest.fail(f"Failed to save to Google Sheets: {str(e)}")

if __name__ == "__main__":
    test_sheets_manager() 