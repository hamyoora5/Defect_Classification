import psycopg2
import os

def init_db():
    # 1. DB 연결 설정 (PostgreSQL)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "15432")
    DB_NAME = os.getenv("DB_NAME", "defect_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "1234")
    
    # 2. SQL 파일 읽기
    SQL_FILE = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(SQL_FILE):
        print(f"Error: {SQL_FILE} not found.")
        return
        
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_query = f.read()
        
    # 3. DB 접속 및 실행
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print(f"[{DB_HOST}:{DB_PORT}] Initializing database '{DB_NAME}'...")
        cursor.execute(sql_query)
        print("Database schema created successfully.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == "__main__":
    init_db()
