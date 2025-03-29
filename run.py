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

from src.cli import ShortFactoryCLI, get_user_input
from src.core.content.content_generator import ContentGenerator
from src.core.visual.visual_director import VisualDirector
from src.core.audio.narration_generator import NarrationGenerator
from src.core.video.video_assembler import VideoAssembler
from src.utils.logger import Logger
import uuid


def main():
    """CLI의 메인 진입점입니다."""
    try:
        print("environment variables loaded: ", os.getenv("GOOGLE_API_KEY"))
        print("\n=== Short Factory ===")        
        while True:
            try:
                # Get creator first
                creator = get_user_input()
                
                # Get model choice
                print("\n=== Select Model ===")
                print("1. Gemini")
                print("2. GPT-4")
                while True:
                    try:
                        model_choice = int(input("\nSelect a model (1-2): "))
                        if 1 <= model_choice <= 2:
                            model = "gemini" if model_choice == 1 else "gpt-4o"
                            break
                        print("Invalid choice. Please try again.")
                    except ValueError:
                        print("Please enter a valid number.")
                
                # Initialize CLI with creator and model
                cli = ShortFactoryCLI(creator=creator, model=model)
                cli.create_short()
            except ValueError:
                print("Please enter a valid number.")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
                
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n오류가 발생했습니다: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 