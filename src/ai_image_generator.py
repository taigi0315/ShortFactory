import os
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import io
import requests
from .utils.logger import Logger

class AIImageGenerator:
    def __init__(self):
        self._setup_api()
        self.logger = Logger()
    
    def _setup_api(self):
        """Gemini API 설정"""
        # Load environment variables from .env file in project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        load_dotenv(os.path.join(project_root, '.env'))
        
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
        self.logger.section("AI 이미지 생성")
        self.logger.info(f"프롬프트: {prompt}")
        self.logger.info(f"출력 경로: {output_path}")
        
        try:
            self.logger.process("OpenAI API에 이미지 생성 요청 중...")
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "dall-e-3",
                    "prompt": prompt,
                    "n": 1,
                    "size": "1792x1024",
                    "quality": "standard",
                    "style": "vivid"
                }
            )
            
            if response.status_code != 200:
                self.logger.error(f"API 요청 실패: {response.text}")
                raise Exception(f"API 요청 실패: {response.text}")
            
            image_url = response.json()["data"][0]["url"]
            self.logger.success(f"이미지 URL 생성 완료: {image_url}")
            
            self.logger.process("이미지 다운로드 중...")
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                self.logger.error(f"이미지 다운로드 실패: {image_response.text}")
                raise Exception(f"이미지 다운로드 실패: {image_response.text}")
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(image_response.content)
            
            self.logger.success(f"이미지 저장 완료: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"이미지 생성 중 오류 발생: {str(e)}")
            return self._create_black_screen()
    
    def generate_video(self, prompt: str, duration: float = 3.0, output_path: Optional[str] = None) -> str:
        """프롬프트를 기반으로 비디오를 생성합니다."""
        try:
            # 비디오 생성 요청
            response = self.model.generate_content(prompt)
            
            # 응답에서 비디오 데이터 추출
            if hasattr(response, 'text'):
                # 임시로 검은 화면 비디오 생성
                return self._create_black_screen_video(duration)
            
            raise ValueError("비디오 생성 실패: 응답에 비디오 데이터가 없습니다.")
            
        except Exception as e:
            print(f"비디오 생성 중 오류 발생: {str(e)}")
            return self._create_black_screen_video(duration)
    
    def _create_black_screen(self):
        """검은 화면 이미지를 생성합니다."""
        try:
            # 임시 더미 이미지 생성
            dummy_path = "data/images/dummy.png"
            os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
            dummy_image = Image.new('RGB', (1080, 1920), color='black')
            dummy_image.save(dummy_path, format='PNG')
            return dummy_path
        except Exception as e:
            print(f"검은 화면 이미지 생성 중 오류 발생: {str(e)}")
            return "data/images/dummy.png"
    
    def _create_black_screen_video(self, duration: float):
        """검은 화면 비디오를 생성합니다."""
        try:
            # 검은 화면 이미지 생성
            black_screen = self._create_black_screen()
            
            # 이미지를 비디오로 변환
            dummy_path = "data/videos/dummy.mp4"
            os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
            
            # 이미지를 비디오로 변환
            import ffmpeg
            
            # 입력 이미지 스트림 생성
            stream = ffmpeg.input(black_screen, t=duration)
            
            # 출력 비디오 스트림 생성
            stream = ffmpeg.output(stream, dummy_path, vcodec='libx264', r=30)
            
            # 비디오 생성
            ffmpeg.run(stream, overwrite_output=True)
            
            return dummy_path
        except Exception as e:
            print(f"검은 화면 비디오 생성 중 오류 발생: {str(e)}")
            return "data/videos/dummy.mp4" 