from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import os
import shutil
import psycopg2
import sys
from datetime import datetime

# 모델 및 추론 로직 추가 경로 포함
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from model.inference_yolo import YOLOInference

app = FastAPI(title="Smart Factory Vision AI Result API")

# 1. 환경 설정 및 초기화
# YOLO 학습 결과 경로로 변경
MODEL_PATH = os.getenv("MODEL_PATH", "d:/docker_data/Defect_Classification/runs/detect/defect_yolo_final_optimized/weights/last.pt")
IMG_SAVE_DIR = "d:/docker_data/Defect_Classification/data/results"
os.makedirs(IMG_SAVE_DIR, exist_ok=True)

# 추론 엔진 초기화 (USER 요청에 따라 CPU 환경으로 설정)
inference = YOLOInference(MODEL_PATH, device='cpu')

# 2. 전역 변수 및 Batch ID 설정
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--batch_id", default="", help="Manual Batch ID")
args, unknown = parser.parse_known_args()

# 한국 시간 기준 (UTC+9)
from datetime import timedelta, timezone
KST_TZ = timezone(timedelta(hours=9))

if args.batch_id and args.batch_id.strip():
    CURRENT_BATCH_ID = args.batch_id.strip()
else:
    CURRENT_BATCH_ID = f"LOT-{datetime.now(KST_TZ).strftime('%Y%m%d-%H%M%S')}"

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
    
    # 3. 결과 DB 저장
    import json
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            KST = timezone(timedelta(hours=9))
            now_local = datetime.now(KST)
            
            # 전역에서 생성된 CURRENT_BATCH_ID 사용
            batch_id = CURRENT_BATCH_ID
            
            insert_query = """
            INSERT INTO inspection_results 
            (product_id, image_path, result_image_path, quality, is_defective, confidence, defect_type, bbox, inspection_time, batch_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                file.filename,
                temp_path,
                prediction.get('result_image'),
                prediction['label'],
                prediction['is_defective'],
                prediction['confidence'],
                prediction['defect_type'],
                json.dumps(prediction.get('detections', [])),
                now_local,
                batch_id # 관리 번호 추가
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
