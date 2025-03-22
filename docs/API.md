# Short Factory API 문서

## 1. ContentGenerator

### 1.1 generate_content
```python
def generate_content(topic: str, target_audience: str, mood: str) -> Dict
```

주제, 대상 청중, 분위기를 기반으로 콘텐츠 계획을 생성합니다.

**파라미터:**
- `topic`: 비디오의 주제
- `target_audience`: 대상 청중 (general, educational, entertainment)
- `mood`: 비디오의 분위기 (energetic, peaceful, funny)

**반환값:**
```python
{
    "story": str,  # 전체 스토리 설명
    "scenes": [
        {
            "scene_id": str,  # 씬 식별자
            "description": str,  # 씬 설명
            "action_elements": List[str],  # 동작 요소 목록
            "transition_type": str,  # 전환 효과
            "narration": str,  # 내레이션 스크립트
            "mood": str,  # 씬 분위기
            "image": {
                "style": str,  # 시각적 스타일
                "main_element": str,  # 주요 요소
                "composition": str,  # 카메라 구성
                "background_scene": str,  # 배경 장면
                "color_palette": str  # 색상 팔레트
            },
            "short_caption": str,  # 자막
            "animation_instructions": {
                "primary_motion": str,  # 주요 애니메이션
                "secondary_motion": str,  # 보조 애니메이션
                "text_animation": str  # 텍스트 애니메이션
            },
            "sound_effect": {
                "description": str  # 효과음 설명
            },
            "duration": float  # 씬 길이 (초)
        }
    ],
    "scene_contrast_notes": str,  # 씬 간 대비 지시사항
    "background_music": {
        "mood": str,  # 음악 분위기
        "description": str,  # 음악 설명
        "energy_level": str,  # 에너지 레벨
        "tempo_shifts": str  # 템포 변화 지점
    },
    "educational_elements": {
        "vocabulary_words": List[str],  # 어휘 단어
        "definition_overlays": List[str],  # 정의 오버레이
        "learning_objective": str,  # 학습 목표
        "visual_demonstrations": List[str]  # 시각적 데모
    },
    "dynamic_elements": {
        "scene_variety": str,  # 씬 다양성
        "movement_intensity": str,  # 움직임 강도
        "visual_hooks": List[str]  # 시각적 훅
    }
}
```

## 2. ScriptGenerator

### 2.1 generate_script
```python
def generate_script(config: ScriptConfig) -> str
```

콘텐츠 계획을 기반으로 내레이션 스크립트를 생성합니다.

**파라미터:**
```python
class ScriptConfig:
    topic: str
    target_audience: str
    mood: str
    tone: str
    duration: int
```

**반환값:**
- 생성된 스크립트 문자열 (효과음 마커 포함)

## 3. VisualSelector

### 3.1 select_visuals
```python
def select_visuals(script: str, topic: str, target_audience: str, mood: str) -> List[Dict]
```

스크립트에 맞는 시각적 에셋을 선택/생성합니다.

**파라미터:**
- `script`: 내레이션 스크립트
- `topic`: 비디오 주제
- `target_audience`: 대상 청중
- `mood`: 비디오 분위기

**반환값:**
```python
[
    {
        "type": str,  # "IMAGE" 또는 "VIDEO"
        "content": str,  # 파일 경로 또는 URL
        "duration": float,  # 지속 시간 (초)
        "timing": float,  # 시작 시간 (초)
        "style": str,  # 시각적 스타일
        "source_type": str,  # "ai_generated" 또는 "web_search"
        "source_url": Optional[str]  # 원본 URL (있는 경우)
    }
]
```

## 4. AudioGenerator

### 4.1 generate_audio
```python
def generate_audio(script: str, topic: str, target_audience: str, mood: str) -> List[Dict]
```

스크립트를 기반으로 오디오 에셋을 생성합니다.

**파라미터:**
- `script`: 내레이션 스크립트
- `topic`: 비디오 주제
- `target_audience`: 대상 청중
- `mood`: 비디오 분위기

**반환값:**
```python
[
    {
        "type": str,  # "NARRATION" 또는 "SOUND_EFFECT"
        "content": str,  # 오디오 파일 경로
        "timing": float,  # 시작 시간 (초)
        "duration": float,  # 지속 시간 (초)
        "metadata": Dict  # 추가 메타데이터 (음성, 볼륨 등)
    }
]
```

## 5. VideoAssembler

### 5.1 assemble_video
```python
def assemble_video(visual_assets: List[Dict], audio_assets: List[Dict]) -> str
```

시각적/오디오 에셋을 조합하여 최종 비디오를 생성합니다.

**파라미터:**
- `visual_assets`: 시각적 에셋 목록
- `audio_assets`: 오디오 에셋 목록

**반환값:**
- 생성된 비디오 파일의 경로

## 6. Database

### 6.1 create_content
```python
def create_content(
    topic: str,
    target_audience: str,
    mood: str,
    content_plan: Dict,
    script: str,
    narration: Dict,
    sound_effects: List[Dict],
    visuals: List[Dict]
) -> str
```

새로운 콘텐츠 생성 기록을 데이터베이스에 저장합니다.

**파라미터:**
- `topic`: 비디오 주제
- `target_audience`: 대상 청중
- `mood`: 비디오 분위기
- `content_plan`: 콘텐츠 계획
- `script`: 내레이션 스크립트
- `narration`: 내레이션 정보
- `sound_effects`: 효과음 목록
- `visuals`: 시각적 에셋 목록

**반환값:**
- 생성된 콘텐츠의 고유 ID

### 6.2 update_content_status
```python
def update_content_status(content_id: str, status: str, final_video_path: Optional[str] = None)
```

콘텐츠의 상태를 업데이트합니다.

**파라미터:**
- `content_id`: 콘텐츠 ID
- `status`: 새로운 상태 ("pending", "processing", "completed", "failed")
- `final_video_path`: 최종 비디오 파일 경로 (선택사항) 