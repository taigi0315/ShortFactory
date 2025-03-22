"""데이터베이스 관련 유틸리티 함수를 제공합니다."""

import sqlite3
from typing import List, Dict, Any
import os

def get_db_path() -> str:
    """데이터베이스 파일의 경로를 반환합니다."""
    return os.path.join("data", "shorts.db")

def init_db():
    """데이터베이스를 초기화합니다."""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shorts (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL,
        target_audience TEXT NOT NULL,
        mood TEXT NOT NULL,
        content_plan TEXT NOT NULL,
        script TEXT NOT NULL,
        visuals TEXT NOT NULL,
        audio TEXT NOT NULL,
        video_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def get_all_shorts() -> List[Dict[str, Any]]:
    """모든 Short 데이터를 조회합니다."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM shorts ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    # JSON 문자열을 딕셔너리로 변환
    shorts = []
    for row in rows:
        short = dict(row)
        short["content_plan"] = eval(short["content_plan"])
        short["script"] = eval(short["script"])
        short["visuals"] = eval(short["visuals"])
        short["audio"] = eval(short["audio"])
        shorts.append(short)
    
    conn.close()
    return shorts

def get_short_by_id(short_id: str) -> Dict[str, Any]:
    """특정 ID의 Short 데이터를 조회합니다."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM shorts WHERE id = ?", (short_id,))
    row = cursor.fetchone()
    
    if row:
        short = dict(row)
        short["content_plan"] = eval(short["content_plan"])
        short["script"] = eval(short["script"])
        short["visuals"] = eval(short["visuals"])
        short["audio"] = eval(short["audio"])
        return short
    
    conn.close()
    return None

def save_short(short_data: Dict[str, Any]):
    """Short 데이터를 저장합니다."""
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    
    # 딕셔너리를 문자열로 변환
    data = {
        "id": short_data["id"],
        "topic": short_data["topic"],
        "target_audience": short_data["target_audience"],
        "mood": short_data["mood"],
        "content_plan": str(short_data["content_plan"]),
        "script": str(short_data["script"]),
        "visuals": str(short_data["visuals"]),
        "audio": str(short_data["audio"]),
        "video_path": short_data.get("video_path")
    }
    
    cursor.execute("""
    INSERT OR REPLACE INTO shorts 
    (id, topic, target_audience, mood, content_plan, script, visuals, audio, video_path)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["id"], data["topic"], data["target_audience"], data["mood"],
        data["content_plan"], data["script"], data["visuals"], data["audio"],
        data["video_path"]
    ))
    
    conn.commit()
    conn.close() 