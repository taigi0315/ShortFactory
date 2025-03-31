# Short Factory

An AI-powered YouTube Shorts Automated Generation Tool

## Overview

Short Factory is an advanced automation tool that generates YouTube Shorts by orchestrating multiple AI services and components. It creates engaging short-form video content by combining AI-generated scripts, narration, images, and music into a cohesive video output.

## Core Features

- 🤖 AI-driven Content Planning & Generation
- 🎙️ Natural Language Narration Generation
- 🎨 AI Image Generation & Processing
- 🎬 Automated Video Assembly
- 🔊 Text-to-Speech with ElevenLabs
- 📊 Content Performance Analytics
- 📝 Version Control & History Management

## Technical Architecture

### Component Overview

```
ShortFactory/
├── src/
│   ├── core/
│   │   ├── content/
│   │   │   ├── content_generator.py    # Content planning & generation
│   │   │   ├── content_validator.py    # Content validation & rules
│   │   │   └── content_optimizer.py    # SEO & engagement optimization
│   │   ├── audio/
│   │   │   ├── audio_generator.py      # TTS & audio processing
│   │   │   ├── audio_mixer.py         # Audio mixing & effects
│   │   │   └── voice_manager.py       # Voice selection & management
│   │   ├── video/
│   │   │   ├── video_assembler.py     # Video assembly & processing
│   │   │   ├── scene_manager.py       # Scene composition
│   │   │   └── effect_processor.py    # Visual effects & transitions
│   │   └── image/
│   │       ├── image_generator.py     # AI image generation
│   │       └── image_processor.py     # Image processing & optimization
│   ├── utils/
│   │   ├── logger.py                 # Logging system
│   │   ├── config_manager.py         # Configuration management
│   │   └── error_handler.py          # Error handling & recovery
│   └── api/
│       ├── openai_client.py          # OpenAI API integration
│       ├── elevenlabs_client.py      # ElevenLabs API integration
│       └── youtube_client.py         # YouTube API integration
├── data/
│   ├── templates/                    # Content templates
│   ├── prompts/                      # AI prompts
│   ├── output/                       # Generated content
│   └── assets/                       # Static assets
└── config/
    ├── settings.json                 # Global settings
    └── api_config.json              # API configurations
```

### Process Flow

1. **Content Generation**
   - Input processing & validation
   - Content plan generation using GPT-4
   - Scene breakdown & script generation
   - Content optimization & SEO enhancement

2. **Audio Processing**
   - Script to speech conversion (ElevenLabs)
   - Audio normalization & enhancement
   - Background music & sound effects
   - Multi-track audio mixing

3. **Visual Generation**
   - Scene-by-scene image generation
   - Image processing & optimization
   - Visual effects application
   - Frame composition & styling

4. **Video Assembly**
   - Scene composition & sequencing
   - Audio-video synchronization
   - Transition effects
   - Final rendering & optimization

## Technical Specifications

### Video Processing
- Resolution: 1080x1920 (9:16 aspect ratio)
- Framerate: 30 fps
- Codec: H.264
- Format: MP4
- Bitrate: Variable (target quality-based)

### Audio Processing
- Sample Rate: 44.1 kHz
- Channels: Stereo
- Format: AAC
- Bitrate: 192 kbps

### Performance Optimization
- Parallel processing for scene generation
- Caching system for frequently used assets
- Efficient memory management for large files
- Progressive rendering for long videos

## Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/ShortFactory.git
cd ShortFactory
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

## Usage

### Command Line Interface
```bash
python run.py --topic "Topic" --audience "target_audience" --mood "mood" --style "style"
```

### Python API
```python
from src.core.content import ContentGenerator
from src.core.video import VideoAssembler
from src.core.audio import AudioGenerator

# Initialize components
content_gen = ContentGenerator()
audio_gen = AudioGenerator()
video_assembler = VideoAssembler()

# Generate content
content_plan = content_gen.generate(
    topic="Science Facts",
    audience="educational",
    mood="energetic",
    style="modern"
)

# Generate audio
audio_assets = audio_gen.create_audio(content_plan)

# Assemble video
final_video = video_assembler.create_video(
    content_plan=content_plan,
    audio_assets=audio_assets
)
```

## Configuration

### Video Settings
```json
{
    "video": {
        "resolution": {
            "width": 1080,
            "height": 1920
        },
        "fps": 30,
        "max_duration": 60,
        "min_duration": 15
    },
    "audio": {
        "sample_rate": 44100,
        "channels": 2,
        "bitrate": "192k"
    }
}
```

## Error Handling

The system implements comprehensive error handling:
- API failure recovery
- Resource cleanup
- Transaction rollback
- Detailed logging
- Error reporting

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Project Maintainer - [@yourusername](https://github.com/yourusername)

Project Link: [https://github.com/yourusername/ShortFactory](https://github.com/yourusername/ShortFactory) 