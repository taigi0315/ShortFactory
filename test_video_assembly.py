from src.video_assembler import VideoAssembler

def test_video_assembly():
    task_id = "3b58d553-9e1d-4d42-b241-951a0916a505"
    content_id = "test_video"
    
    # 테스트용 콘텐츠 데이터 생성
    content_data = {
        "hook": {
            "duration_seconds": 4,
            "image_path": f"data/{task_id}/images/hook.png",
            "audio_path": f"data/{task_id}/narration/hook.mp3"
        },
        "scenes": [
            {
                "duration_seconds": 10,
                "image_path": f"data/{task_id}/images/scene_1.png",
                "audio_path": f"data/{task_id}/narration/scene_1.mp3"
            },
            {
                "duration_seconds": 12,
                "image_path": f"data/{task_id}/images/scene_2.png",
                "audio_path": f"data/{task_id}/narration/scene_2.mp3"
            },
            {
                "duration_seconds": 15,
                "image_path": f"data/{task_id}/images/scene_3.png",
                "audio_path": f"data/{task_id}/narration/scene_3.mp3"
            },
            {
                "duration_seconds": 13,
                "image_path": f"data/{task_id}/images/scene_4.png",
                "audio_path": f"data/{task_id}/narration/scene_4.mp3"
            }
        ],
        "conclusion": {
            "duration_seconds": 7,
            "image_path": f"data/{task_id}/images/conclusion.png",
            "audio_path": f"data/{task_id}/narration/conclusion.mp3"
        }
    }
    
    # 비디오 조립 실행
    assembler = VideoAssembler(task_id)
    output_path = assembler.assemble_video(content_id, content_data)
    print(f"비디오가 생성되었습니다: {output_path}")

if __name__ == "__main__":
    test_video_assembly() 