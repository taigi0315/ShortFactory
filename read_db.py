"""데이터베이스 내용을 파일처럼 읽어서 표시합니다."""

import sqlite3
import json
from src.db_utils import get_db_path

def read_db():
    """데이터베이스 내용을 읽어서 JSON 형식으로 반환합니다."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
    cursor = conn.cursor()
    
    # 모든 레코드 조회
    cursor.execute("SELECT * FROM shorts ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    # 결과를 딕셔너리 리스트로 변환
    shorts = []
    for row in rows:
        short = dict(row)
        # 문자열로 저장된 데이터를 파이썬 객체로 변환
        short["content_plan"] = eval(short["content_plan"])
        short["script"] = eval(short["script"])
        short["visuals"] = eval(short["visuals"])
        short["audio"] = eval(short["audio"])
        shorts.append(short)
    
    conn.close()
    return shorts

if __name__ == "__main__":
    shorts = read_db()
    print(json.dumps(shorts, indent=2, ensure_ascii=False)) 