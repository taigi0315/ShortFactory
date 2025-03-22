"""데이터베이스를 초기화하는 스크립트입니다."""

from src.db_utils import init_db

if __name__ == "__main__":
    print("데이터베이스를 초기화합니다...")
    init_db()
    print("초기화가 완료되었습니다.") 