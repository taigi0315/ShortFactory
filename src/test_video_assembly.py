import os
from video_assembler_moviepy import VideoAssembler

def test_video_assembly():
    # 테스트용 task_id
    task_id = "test_task"
    
    # 테스트용 content_data
    content_data = {
        "hook": {
            "duration": 10.0,
            "text": "Hook scene"
        },
        "scenes": [
            {
                "duration": 15.0,
                "text": "Scene 1"
            },
            {
                "duration": 15.0,
                "text": "Scene 2"
            }
        ],
        "conclusion": {
            "duration": 10.0,
            "text": "Conclusion scene"
        }
    }
    
    # 테스트용 이미지와 오디오 파일 생성
    test_dir = os.path.join("data", task_id)
    os.makedirs(os.path.join(test_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(test_dir, "narration"), exist_ok=True)
    
    # 테스트용 이미지 생성 (검은색 이미지)
    from PIL import Image
    import numpy as np
    
    # 각 장면별 이미지 생성
    scenes = ["hook", "scene_1", "scene_2", "conclusion"]
    for scene in scenes:
        # 이미지 생성 (1280x720 검은색 이미지)
        img = Image.fromarray(np.zeros((720, 1280, 3), dtype=np.uint8))
        img.save(os.path.join(test_dir, "images", f"{scene}.png"))
        
        # 오디오 파일 생성 (무음)
        os.system(f"ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 10 -q:a 9 -acodec libmp3lame {os.path.join(test_dir, 'narration', f'{scene}.mp3')}")
    
    # VideoAssembler 인스턴스 생성 및 비디오 생성
    assembler = VideoAssembler(task_id)
    output_path = assembler.assemble_video("test_output", content_data)
    
    print(f"Generated video saved at: {output_path}")

if __name__ == "__main__":
    test_video_assembly() 