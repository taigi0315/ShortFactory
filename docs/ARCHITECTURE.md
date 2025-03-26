# ShortFactory System Architecture

## System Overview

```mermaid
graph TD
    A[User Input] -->|subject, detail, image_style| B[ContentGenerator]
    B -->|content_plan| C[ScriptGenerator]
    B -->|visual_requirements| D[VisualSelector]
    B -->|music_style| E[AudioGenerator]
    C -->|script| F[VideoAssembler]
    D -->|visual_assets| F
    E -->|audio_assets| F
    F -->|final_video| G[Output]
    
    D -->|prompt_request| H[PromptGenerator]
    H -->|image_prompt| I[ImageGenerator]
    H -->|video_prompt| J[VideoGenerator]
    H -->|search_query| K[WebImageSearch]
    
    I -->|generated_image| D
    J -->|generated_video| D
    K -->|found_image| D
```

## Component Details

### ContentGenerator
```mermaid
classDiagram
    class ContentGenerator {
        +generate_content_plan(subject, detail, image_style)
        -_create_content_prompt()
        -_get_llm_response()
        -_parse_llm_response()
        -_load_plans()
        -_save_plans()
    }
    
    class ContentPlan {
        +subject: str
        +detail: str
        +image_style: str
        +key_points: list
        +visual_requirements: list
        +music_style: str
    }
    
    ContentGenerator --> ContentPlan
```

### VisualSelector
```mermaid
classDiagram
    class VisualSelector {
        +select_visuals(script)
        -_create_visuals_for_script()
        -_load_visuals()
        -_save_visuals()
        -_determine_visual_type()
        -_get_visual_from_source()
    }
    
    class VisualAsset {
        +type: str
        +content: str
        +timing: float
        +style: str
        +duration: float
        +source_type: str
        +source_url: str
    }
    
    class VisualSource {
        <<enumeration>>
        WEB_SEARCH
        AI_IMAGE
        AI_VIDEO
    }
    
    VisualSelector --> VisualAsset
    VisualSelector --> VisualSource
```

### PromptGenerator
```mermaid
classDiagram
    class PromptGenerator {
        +generate_prompt(story, style)
        -_create_prompt_template()
        -_format_prompt()
    }
    
    class PromptTemplate {
        +story: str
        +style: str
    }
    
    PromptGenerator --> PromptTemplate
```

### ImageGenerator
```mermaid
classDiagram
    class ImageGenerator {
        +generate_image(prompt)
        -_validate_prompt()
        -_call_ai_service()
        -_process_response()
    }
    
    class ImageResult {
        +image_url: str
        +metadata: dict
        +generation_time: float
    }
    
    ImageGenerator --> ImageResult
```

### VideoGenerator
```mermaid
classDiagram
    class VideoGenerator {
        +generate_video(prompt)
        -_validate_prompt()
        -_call_ai_service()
        -_process_response()
    }
    
    class VideoResult {
        +video_url: str
        +duration: float
        +metadata: dict
        +generation_time: float
    }
    
    VideoGenerator --> VideoResult
```

### WebImageSearch
```mermaid
classDiagram
    class WebImageSearch {
        +search_images(query)
        +find_similar_images(image_url)
        -_validate_query()
        -_call_search_api()
        -_process_results()
    }
    
    class SearchResult {
        +image_url: str
        +source_url: str
        +similarity_score: float
    }
    
    WebImageSearch --> SearchResult
```

### AudioGenerator
```mermaid
classDiagram
    class AudioGenerator {
        +generate_audio(script)
        -_create_audio_info()
        -_load_audio_info()
        -_save_audio_info()
    }
    
    class AudioInfo {
        +file_path: str
        +duration: float
        +background_music: str
        +voice_settings: dict
    }
    
    AudioGenerator --> AudioInfo
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant ContentGenerator
    participant LLM
    participant VisualSelector
    participant PromptGenerator
    participant ImageGenerator
    participant VideoGenerator
    participant WebImageSearch
    participant AudioGenerator
    participant VideoAssembler
    
    User->>ContentGenerator: generate_content_plan(subject, ...)
    ContentGenerator->>LLM: _get_llm_response(prompt)
    LLM-->>ContentGenerator: content_plan
    ContentGenerator->>VisualSelector: select_visuals(content_plan)
    
    VisualSelector->>PromptGenerator: generate_image_prompt(story, mood)
    PromptGenerator->>LLM: _get_llm_response(prompt)
    LLM-->>PromptGenerator: image_prompt
    PromptGenerator-->>VisualSelector: image_prompt
    
    VisualSelector->>ImageGenerator: generate_image(prompt)
    ImageGenerator-->>VisualSelector: generated_image
    
    VisualSelector->>PromptGenerator: generate_video_prompt(story, mood)
    PromptGenerator->>LLM: _get_llm_response(prompt)
    LLM-->>PromptGenerator: video_prompt
    PromptGenerator-->>VisualSelector: video_prompt
    
    VisualSelector->>VideoGenerator: generate_video(prompt)
    VideoGenerator-->>VisualSelector: generated_video
    
    VisualSelector->>PromptGenerator: generate_search_query(story, mood)
    PromptGenerator->>LLM: _get_llm_response(prompt)
    LLM-->>PromptGenerator: search_query
    PromptGenerator-->>VisualSelector: search_query
    
    VisualSelector->>WebImageSearch: search_images(query)
    WebImageSearch-->>VisualSelector: found_images
    
    ContentGenerator->>AudioGenerator: generate_audio(content_plan)
    VisualSelector-->>VideoAssembler: visual_assets
    AudioGenerator-->>VideoAssembler: audio_assets
    VideoAssembler-->>User: final_video
```

## Storage Structure

```mermaid
graph LR
    A[data/] --> B[content_plans.json]
    A --> C[visuals.json]
    A --> D[audio.json]
    A --> E[audio_files/]
    A --> F[generated_images/]
    A --> G[generated_videos/]
    A --> H[prompts.json]
```

## Component Parameters

### ContentGenerator
- Input:
  - subject: str (e.g., "Interesting facts about Octopuses")
  - detail: str (additional description)
  - image_style: str (visual style)
- Output:
  - content_plan: Dict containing hook, key_points, conclusion, visual_requirements, music_style

### VisualSelector
- Input:
  - script: str (from ContentGenerator)
- Output:
  - List[Dict] containing visual assets with type, content, timing, style, duration, source_type, source_url

### PromptGenerator
- Input:
  - story: str (content to visualize)
  - style: str (visual style)
- Output:
  - image_prompt: str (for AI image generation)
  - video_prompt: str (for AI video generation)
  - search_query: str (for web image search)

### ImageGenerator
- Input:
  - prompt: str (from PromptGenerator)
- Output:
  - ImageResult containing image_url and metadata

### VideoGenerator
- Input:
  - prompt: str (from PromptGenerator)
- Output:
  - VideoResult containing video_url and metadata

### WebImageSearch
- Input:
  - query: str (from PromptGenerator)
  - image_url: str (optional, for similar image search)
- Output:
  - List[SearchResult] containing matching images

### AudioGenerator
- Input:
  - script: str (from ContentGenerator)
- Output:
  - Dict containing audio_info with file_path, duration, background_music, voice_settings 