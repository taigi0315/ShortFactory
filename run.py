#!/usr/bin/env python3
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.cli import main

if __name__ == "__main__":
    main() 