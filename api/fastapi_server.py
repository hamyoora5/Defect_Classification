from fastapi import FastAPI, HTTPException, UploadFile, File
import os
import shutil
import psycopg2
import sys
import json
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from model.inference_yolo import YOLOInference

app = FastAPI()

# 설정 (3시간 긴급 복구 모델 경로로 변경)
MODEL_PATH = "d:/docker_data/Defect_Classification/runs/detect/defect_yolo_fast_track/weights/last.pt"
IMG_SAVE_DIR = "d:/docker_data/Defect_Classification/data/results"
BATCH_FILE = "d:/docker_data/Defect_Classification/active_batch.txt"
os.makedirs(IMG_SAVE_DIR, exist_ok=True)

inference = YOLOInference(MODEL_PATH, device='cpu')

def get_db_connection():
    try:
        conn = psycopg2.connect(host="localhost", port="15432", database="defect_db", user="postgres", password="1234")
        return conn
    except Exception as e:
        print(f"DB Connection Error: {e}")
        return None

def get_active_batch():
    if os.path.exists(BATCH_FILE):
        with open(BATCH_FILE, "r", encoding='utf-8') as f:
            return f.read().strip()
    return "AUTO-BATCH"

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    file_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_path = os.path.join(IMG_SAVE_DIR, f"temp_{file_id}_{file.filename}")
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    prediction = inference.predict(temp_path)
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            # [필승] 타임존 정보를 완전히 제거하여, Postgres가 UTC로 비틀지 못하게 '절대 수치'만 전송
            # 지금이 15:30분이면, (15, 30)이라는 숫자 데이터 그대로만 보냄
            now_kst_naive = datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)
            batch_id = get_active_batch()
            
            insert_query = """
            INSERT INTO inspection_results 
            (product_id, image_path, result_image_path, quality, is_defective, confidence, defect_type, bbox, inspection_time, batch_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                file.filename, temp_path, prediction.get('result_image'),
                prediction['label'], prediction['is_defective'],
                prediction['confidence'], prediction['defect_type'],
                json.dumps(prediction.get('detections', [])),
                now_kst_naive, batch_id
            ))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"DB Error: {e}")
            conn.rollback()
    
    return {"prediction": prediction}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
