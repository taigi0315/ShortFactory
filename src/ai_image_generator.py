import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io

class AIImageGenerator:
    def __init__(self):
        self._setup_api()
    
    def _setup_api(self):
        """Gemini API 설정"""
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "Google API key not found. Please set the GOOGLE_API_KEY environment variable "
                "in your .env file or system environment variables."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_image(self, prompt: str, output_path: Optional[str] = None) -> str:
        """프롬프트를 기반으로 이미지를 생성합니다."""
        try:
            # 이미지 생성 요청
            response = self.model.generate_content(prompt)
            
            # 이미지 데이터 추출
            image_data = response.image
            
            # PIL Image로 변환
            image = Image.open(io.BytesIO(image_data))
            
            # 출력 경로가 지정되지 않은 경우 임시 파일로 저장
            if not output_path:
                output_path = f"data/visuals/generated_{hash(prompt)}.png"
            
            # 이미지 저장
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"이미지 생성 중 오류 발생: {str(e)}")
            # 임시 더미 이미지 생성
            dummy_path = "data/images/dummy.jpg"
            os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
            dummy_image = Image.new('RGB', (1080, 1920), color='white')
            dummy_image.save(dummy_path)
            return dummy_path
    
    def generate_video(self, prompt: str, duration: float = 5.0, output_path: Optional[str] = None) -> str:
        """프롬프트를 기반으로 비디오를 생성합니다."""
        try:
            # 비디오 생성 요청
            response = self.model.generate_content(prompt)
            
            # 비디오 데이터 추출
            video_data = response.video
            
            # 출력 경로가 지정되지 않은 경우 임시 파일로 저장
            if not output_path:
                output_path = f"data/visuals/generated_{hash(prompt)}.mp4"
            
            # 비디오 저장
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(video_data)
            
            return output_path
            
        except Exception as e:
            print(f"비디오 생성 중 오류 발생: {str(e)}")
            # 임시 더미 비디오 생성
            dummy_path = "data/videos/dummy.mp4"
            os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
            # 더미 비디오 파일 생성 로직 추가 필요
            return dummy_path 