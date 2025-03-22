#!/usr/bin/env python3
import os
import sys
import json
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Load environment variables from .env file in project root
load_dotenv(os.path.join(project_root, '.env'))

from src.cli import get_user_input
from src.content_generator import ContentGenerator
from src.visual_director import VisualDirector
from src.audio_generator import AudioGenerator
from src.video_assembler import VideoAssembler
from src.database import Database
from src.utils.logger import Logger
import uuid


def main():
    # 환경 변수 로드
    load_dotenv()
    
    # 로거 초기화
    logger = Logger()
    logger.section("YouTube Short 생성 시작")
    
    # 데이터베이스 초기화
    db = Database()
    
    try:
        # 1. 사용자 입력 받기
        topic, detail, target_audience, mood = get_user_input()
        task_id = str(uuid.uuid4())

        logger.info(f"주제: {topic}")
        logger.info(f"대상: {target_audience}")
        logger.info(f"분위기: {mood}")
        
        # 2. 콘텐츠 생성
        logger.subsection("콘텐츠 생성")
        content_gen = ContentGenerator(task_id)
        content_plan = content_gen.generate_content(topic, detail, target_audience, mood)
        
        # 3. 시각적 에셋 생성
        logger.subsection("시각적 에셋 생성")
        visual_director = VisualDirector(task_id)
        visuals = visual_director.create_visuals(content_plan, target_audience, mood)
        
        # 4. 오디오 생성
        logger.subsection("오디오 에셋 생성")
        # audio_gen = AudioGenerator()
        # audio_assets = audio_gen.generate_audio_assets(content_plan)
        
        # 5. 비디오 조립
        logger.subsection("비디오 생성")
        # video_assembler = VideoAssembler()
        # final_video_path = video_assembler.assemble_video(visuals, audio_assets)
        
        # 6. 데이터베이스에 저장
        logger.subsection("데이터베이스에 저장")
        content_id = db.create_content(
            topic=topic,
            target_audience=target_audience,
            mood=mood,
            content_plan=content_plan,
            # narration=audio_assets["narration"],
            # sound_effects=audio_assets["sound_effects"],
            narration="",
            sound_effects=[],
            visuals=visuals
        )
        
        # 7. 상태 업데이트
        logger.subsection("상태 업데이트")
        db.update_content_status(content_id, "completed", final_video_path)
        
        logger.success(f"YouTube Short 생성 완료: {final_video_path}")
        
        # 8. 생성된 콘텐츠 정보 출력
        logger.subsection("생성된 콘텐츠 정보 출력")
        content = db.get_content(content_id)
        print("\n[+] 생성된 콘텐츠 정보:")
        print(f"주제: {content['topic']}")
        print(f"대상: {content['target_audience']}")
        print(f"분위기: {content['mood']}")
        print(f"생성일: {content['created_at']}")
        print("\n[+] 콘텐츠 계획:")
        print(json.dumps(content['content_plan'], ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"YouTube Short 생성 중 오류 발생: {str(e)}")
        if 'content_id' in locals():
            db.update_content_status(content_id, "failed")

if __name__ == "__main__":
    main() 