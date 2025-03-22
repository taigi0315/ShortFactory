# ShortFactory

YouTube Shorts 자동 생성 시스템

## 기능

- 스크립트 생성 (LLM 기반)
- 시각적 자산 선택
- 오디오 생성 (TTS)
- 비디오 조립
- 자막 생성
- 스타일 커스터마이징
- 분석 통합

## 설치 방법

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

## 실행 방법

```bash
# 개발 서버 실행
uvicorn src.main:app --reload
```

## 테스트 실행

```bash
pytest
```

## 프로젝트 구조

```
ShortFactory/
├── src/           # 소스 코드
├── tests/         # 테스트 코드
├── requirements.txt
└── README.md
``` 