from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import shutil
import psycopg2
import sys
from datetime import datetime

# 모델 및 추론 로직 추가 경로 포함
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from model.inference import DefectInference

app = FastAPI(title="Smart Factory Vision AI Result API")

# 1. 환경 설정 및 초기화
MODEL_PATH = os.getenv("MODEL_PATH", "d:/docker_data/Defect_Classification/data/cardoor/model/resnet_binary_model.pth")
IMG_SAVE_DIR = "d:/docker_data/Defect_Classification/data/results"
os.makedirs(IMG_SAVE_DIR, exist_ok=True)

# 추론 엔진 초기화
inference = DefectInference(MODEL_PATH)

# 2. 데이터베이스 연결 함수
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "15432"),
            database=os.getenv("DB_NAME", "defect_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "1234")
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# 3. API 엔드포인트
@app.get("/")
def read_root():
    return {"message": "Smart Factory Vision AI API Server is running."}

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    이미지 파일을 업로드 받아 추론 결과를 반환하고 결과를 DB에 저장함
    """
    # 1. 파일 임시 저장
    file_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_path = os.path.join(IMG_SAVE_DIR, f"temp_{file_id}_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. 모델 추론
    try:
        prediction = inference.predict(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # 3. 결과 DB 저장 (비동기로 권장되나 단순화를 위해 동기 수행)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            insert_query = """
            INSERT INTO inspection_results (product_id, image_path, quality, is_defective, confidence, defect_type, inspection_time)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """
            cursor.execute(insert_query, (
                file.filename,
                temp_path,
                prediction['label'],
                prediction['is_defective'],
                prediction['confidence'],
                prediction['defect_type']
            ))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"DB Insert error: {e}")
            conn.rollback()
            cursor.close()
            conn.close()
    
    return {
        "filename": file.filename,
        "prediction": prediction,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
