# Short Factory

AI를 활용한 YouTube Shorts 자동 생성 도구

## 소개

Short Factory는 주제, 대상 청중, 분위기를 입력받아 YouTube Shorts 형식의 짧은 비디오를 자동으로 생성하는 도구입니다. 
GPT-4를 사용한 콘텐츠 생성, ElevenLabs를 활용한 자연스러운 내레이션, AI 이미지/비디오 생성 등 다양한 AI 기술을 활용하여 
고품질의 Shorts 콘텐츠를 만들어냅니다.

## 주요 기능

- 🤖 AI 기반 콘텐츠 계획 생성
- 📝 자연스러운 내레이션 스크립트 작성
- 🎨 AI 이미지/비디오 생성
- 🔊 ElevenLabs를 활용한 자연스러운 음성 생성
- 🎵 배경음악 및 효과음 추가
- 🎬 자동 비디오 조립
- 💾 생성 이력 관리

## 설치 방법

1. 저장소 클론
```bash
git clone https://github.com/yourusername/ShortFactory.git
cd ShortFactory
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용을 추가합니다:
```
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

## 사용 방법

### CLI 사용

```bash
python run.py
```

실행하면 다음 정보를 입력하라는 프롬프트가 표시됩니다:
1. 비디오 주제
2. 대상 청중 (일반, 교육, 엔터테인먼트)
3. 분위기 (활기찬, 평화로운, 재미있는)

### Python API 사용

```python
from src.content_generator import ContentGenerator
from src.audio_generator import AudioGenerator
from src.video_assembler import VideoAssembler

# 콘텐츠 생성
content_gen = ContentGenerator()
content_plan = content_gen.generate_content(
    topic="수학의 기초",
    target_audience="educational",
    mood="energetic"
)

# 오디오 생성
audio_gen = AudioGenerator()
audio_assets = audio_gen.generate_audio(script)

# 비디오 조립
video_assembler = VideoAssembler()
final_video = video_assembler.assemble_video(visuals, audio_assets)
```

## 프로젝트 구조

```
ShortFactory/
├── src/
│   ├── content_generator.py  # 콘텐츠 계획 생성
│   ├── audio_generator.py    # 오디오 생성
│   ├── video_assembler.py    # 비디오 조립
│   └── database.py          # 데이터 저장
├── data/
│   ├── output/              # 생성된 비디오 저장
│   ├── audio_files/         # 오디오 파일 저장
│   └── prompts.json         # AI 프롬프트 저장
├── config/
│   └── settings.json        # 설정 파일
├── docs/
│   ├── DESIGN.md           # 설계 문서
│   └── API.md              # API 문서
├── tests/                  # 테스트 코드
├── requirements.txt        # 의존성 목록
└── run.py                 # 실행 스크립트
```

## 설정

`config/settings.json` 파일에서 다음 설정을 변경할 수 있습니다:

- 비디오 해상도
- FPS
- 음량 설정
- 최대/최소 비디오 길이

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 연락처

프로젝트 관리자 - [@yourusername](https://github.com/yourusername)

프로젝트 링크: [https://github.com/yourusername/ShortFactory](https://github.com/yourusername/ShortFactory) 