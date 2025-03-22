import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class Database:
    def __init__(self, db_path: str = "data/shorts.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """데이터베이스와 테이블을 초기화합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 콘텐츠 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS contents (
            id TEXT PRIMARY KEY,
            topic TEXT NOT NULL,
            target_audience TEXT NOT NULL,
            mood TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            content_plan TEXT NOT NULL,
            script TEXT NOT NULL,
            narration TEXT NOT NULL,
            sound_effects TEXT NOT NULL,
            visuals TEXT NOT NULL,
            final_video_path TEXT,
            status TEXT DEFAULT 'pending'
        )
        ''')
        
        # 이미지 생성 기록 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS image_generations (
            id TEXT PRIMARY KEY,
            content_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            image_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES contents (id)
        )
        ''')
        
        # 비디오 생성 기록 테이블
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_generations (
            id TEXT PRIMARY KEY,
            content_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            video_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES contents (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_content(self, topic: str, target_audience: str, mood: str,
                      content_plan: Dict, script: Dict, narration: str,
                      sound_effects: List[str], visuals: List[Dict]) -> str:
        """새로운 콘텐츠를 생성합니다."""
        content_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO contents (
            id, topic, target_audience, mood, content_plan, script,
            narration, sound_effects, visuals
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_id,
            topic,
            target_audience,
            mood,
            json.dumps(content_plan),
            json.dumps(script),
            narration,
            json.dumps(sound_effects),
            json.dumps(visuals)
        ))
        
        conn.commit()
        conn.close()
        
        return content_id
    
    def add_image_generation(self, content_id: str, prompt: str, image_path: str):
        """이미지 생성 기록을 추가합니다."""
        image_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO image_generations (id, content_id, prompt, image_path)
        VALUES (?, ?, ?, ?)
        ''', (image_id, content_id, prompt, image_path))
        
        conn.commit()
        conn.close()
    
    def add_video_generation(self, content_id: str, prompt: str, video_path: str):
        """비디오 생성 기록을 추가합니다."""
        video_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO video_generations (id, content_id, prompt, video_path)
        VALUES (?, ?, ?, ?)
        ''', (video_id, content_id, prompt, video_path))
        
        conn.commit()
        conn.close()
    
    def update_content_status(self, content_id: str, status: str, final_video_path: Optional[str] = None):
        """콘텐츠 상태를 업데이트합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if final_video_path:
            cursor.execute('''
            UPDATE contents SET status = ?, final_video_path = ?
            WHERE id = ?
            ''', (status, final_video_path, content_id))
        else:
            cursor.execute('''
            UPDATE contents SET status = ?
            WHERE id = ?
            ''', (status, content_id))
        
        conn.commit()
        conn.close()
    
    def get_content(self, content_id: str) -> Optional[Dict]:
        """콘텐츠 정보를 조회합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM contents WHERE id = ?
        ''', (content_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "topic": row[1],
            "target_audience": row[2],
            "mood": row[3],
            "created_at": row[4],
            "content_plan": json.loads(row[5]),
            "script": json.loads(row[6]),
            "narration": row[7],
            "sound_effects": json.loads(row[8]),
            "visuals": json.loads(row[9]),
            "final_video_path": row[10],
            "status": row[11]
        }
    
    def get_all_contents(self) -> List[Dict]:
        """모든 콘텐츠 정보를 조회합니다."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM contents ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "topic": row[1],
            "target_audience": row[2],
            "mood": row[3],
            "created_at": row[4],
            "content_plan": json.loads(row[5]),
            "script": json.loads(row[6]),
            "narration": row[7],
            "sound_effects": json.loads(row[8]),
            "visuals": json.loads(row[9]),
            "final_video_path": row[10],
            "status": row[11]
        } for row in rows] 