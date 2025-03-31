from src.core.video.video_assembler import VideoAssembler
import json
import ffmpeg

def main():
    # 작업 ID와 크리에이터 설정
    task_id = "6390b4b7-794f-4db3-a335-f987441311a6"
    
    creator = "science_fact"
    
    # VideoAssembler 초기화
    assembler = VideoAssembler(task_id, creator)
    
    # 모든 씬을 포함하는 content plan 생성
    content_data = {
        "video_title": "Science Fact Video",
        "video_description": "Assembled science fact video",
        "hashtags": ["science", "fact"],
        "hook": {
            "script": "Hook scene",
            "image_keywords": ["hook"],
            "scene_description": "Hook scene",
            "image_to_video": "Default animation",
            "image_style_name": "hook"
        },
        "scenes": [
            {
                "script": f"Scene {i}",
                "image_keywords": ["science"],
                "scene_description": f"Scene {i}",
                "image_to_video": "Default animation",
                "image_style_name": f"scene_{i}"
            } for i in range(1, 9)  # scenes 1-9
        ],
        "conclusion": {
            "script": "Conclusion scene",
            "image_keywords": ["conclusion"],
            "scene_description": "Conclusion scene",
            "image_to_video": "Default animation",
            "image_style_name": "conclusion"
        }
    }
    
    try:
        # 비디오 조립 실행
        output_path = assembler.assemble_video(
            content_id="test_assembly",
            content_data=content_data
        )
        print(f"비디오 생성 완료: {output_path}")
        
    except ffmpeg.Error as e:
        print(f"FFmpeg 에러:")
        print("stdout:", e.stdout.decode('utf8'))
        print("stderr:", e.stderr.decode('utf8'))
    except Exception as e:
        print(f"일반 에러: {str(e)}")

if __name__ == "__main__":
    main() 