#!/usr/bin/env python3
"""
ShortFactory CLI 실행 스크립트
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables from .env file in project root
load_dotenv(os.path.join(project_root, '.env'))

from src.cli import ShortFactoryCLI
from src.content_generator import ContentGenerator
from src.visual_director import VisualDirector
from src.narration_generator import NarrationGenerator
from src.video_assembler import VideoAssembler
from src.utils.logger import Logger
import uuid


def main():
    """CLI의 메인 진입점입니다."""
    try:
        print("environment variables loaded: ", os.getenv("GOOGLE_API_KEY"))
        cli = ShortFactoryCLI()
        cli.create_short()
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 