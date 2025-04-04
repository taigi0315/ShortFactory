# Short Factory - YouTube Shorts 생성기

## 1. 개요

Short Factory는 AI를 활용하여 YouTube Shorts 형식의 짧은 비디오를 자동으로 생성하는 도구입니다. 
이 도구는 주제, 대상 청중, 분위기를 입력받아 전체적인 스토리, 내레이션 스크립트, 시각적 요소, 오디오를 생성하고 최종적으로 완성된 비디오를 만들어냅니다.

## 2. 시스템 아키텍처

### 2.1 핵심 컴포넌트

1. **ContentGenerator**
   - 전체 콘텐츠 계획 생성
   - LLM을 사용하여 주제에 맞는 스토리 구조화
   - 훅, 주요 포인트, 결론 등 구성요소 생성
   - 상세한 씬별 설명 및 지시사항 생성
   - 교육적 요소 및 동적 요소 정의

2. **ScriptGenerator**
   - 내레이션 스크립트 생성
   - 효과음 마커 추가
   - 스크립트 캐싱 시스템

3. **VisualSelector**
   - 이미지/비디오 에셋 선택
   - AI 이미지/비디오 생성 프롬프트 생성
   - 웹 이미지 검색 통합

4. **AudioGenerator**
   - ElevenLabs를 사용한 내레이션 생성
   - 배경음악 및 효과음 처리
   - 오디오 믹싱

5. **VideoAssembler**
   - 시각적/오디오 에셋 조합
   - 비디오 타임라인 조정
   - 자막 오버레이

6. **Database**
   - SQLite 기반 데이터 저장
   - 콘텐츠 생성 기록 관리
   - 이미지/비디오 생성 이력 추적

### 2.2 데이터 흐름

1. 사용자 입력 (주제, 대상 청중, 분위기)
2. 콘텐츠 계획 생성
3. 스크립트 생성
4. 시각적 에셋 생성/선택
5. 오디오 생성
6. 비디오 조립
7. 최종 비디오 출력

## 3. 기술 스택

### 3.1 핵심 라이브러리
- OpenAI GPT-4: 콘텐츠 생성, 스크립트 작성
- ElevenLabs: 텍스트-음성 변환
- MoviePy: 비디오 편집 및 조립
- SQLite: 데이터 저장

### 3.2 설정
- 비디오 해상도: 1080x1920 (Shorts 최적화)
- FPS: 30
- 기본 음량 설정:
  - 배경음악: 0.3
  - 내레이션: 1.0
  - 효과음: 0.7

## 4. 주요 기능

### 4.1 콘텐츠 생성
- 주제 기반 스토리 구조화
- 대상 청중에 맞는 톤 설정
- 분위기에 맞는 스타일 적용
- 씬별 상세 설명 생성:
  - 씬 ID 및 설명
  - 동작 요소
  - 전환 효과
  - 내레이션 스크립트
  - 분위기
  - 이미지 스타일 및 구성
  - 자막
  - 애니메이션 지시사항
  - 효과음
  - 씬 길이
- 교육적 요소 포함:
  - 어휘 단어
  - 정의 오버레이
  - 학습 목표
  - 시각적 데모
- 동적 요소 정의:
  - 씬 다양성
  - 움직임 강도
  - 시각적 훅

### 4.2 시각적 요소
- AI 이미지 생성
- AI 비디오 생성 (5초 단위)
- 웹 이미지 검색 통합
- 자막 오버레이

### 4.3 오디오 처리
- 자연스러운 내레이션 생성
- 배경음악 선택 및 믹싱
- 효과음 추가

### 4.4 비디오 조립
- 타임라인 자동 조정
- 시각적/오디오 동기화
- 최종 비디오 렌더링

## 5. 데이터 저장 구조

### 5.1 데이터베이스 테이블
1. contents
   - 콘텐츠 기본 정보
   - 생성 계획, 스크립트, 내레이션 등
   - 씬별 상세 정보
   - 교육적 요소
   - 동적 요소

2. image_generations
   - AI 이미지 생성 기록
   - 프롬프트 및 결과물 저장

3. video_generations
   - AI 비디오 생성 기록
   - 프롬프트 및 결과물 저장

## 6. 향후 개선사항

1. 성능 최적화
   - 병렬 처리 도입
   - 캐싱 시스템 강화

2. 기능 확장
   - 다국어 지원
   - 템플릿 시스템
   - 사용자 정의 스타일

3. 품질 향상
   - AI 모델 업그레이드
   - 자동 품질 검사
   - 피드백 시스템 