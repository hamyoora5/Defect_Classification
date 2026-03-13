import os
import requests
import time
import pandas as pd
from datetime import datetime

# 1. 설정
API_URL = "http://localhost:8000/predict"
IMAGE_DIR = "d:/docker_data/Defect_Classification/data/yolo_dataset/images/val"
CSV_PATH = "d:/docker_data/Defect_Classification/validation_defects_list.csv"
INTERVAL_SECONDS = 12

def main():
    print(f"[{datetime.now()}] Mixed Sequence Simulator started.")
    
    # [핵심] 랜덤 대신 CSV 파일 순서대로 이미지 전송
    if not os.path.exists(CSV_PATH):
        print(f"Error: CSV file not found at {CSV_PATH}")
        return
        
    df = pd.read_csv(CSV_PATH)
    image_list = df['product_id'].tolist()
    
    print(f"Loaded sequence for {len(image_list)} images from CSV.")
    
    # 2. 순차적 전송 루프
    try:
        idx = 0
        while True:
            file_name = image_list[idx % len(image_list)]
            img_path = os.path.join(IMAGE_DIR, file_name)
            
            # 실제 파일이 있는지 확인
            if not os.path.exists(img_path):
                print(f"[{datetime.now()}] [WARN] File not found: {file_name}")
                idx += 1
                continue
            
            state = "DEFECT" if "_10_" not in file_name else "NORMAL"
            print(f"[{datetime.now()}] [{idx+1}/{len(image_list)}] [{state}] Sending: {file_name}")
            
            # API 전송
            try:
                with open(img_path, "rb") as f:
                    files = {"file": (file_name, f, "image/jpeg")}
                    response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    label = result['prediction']['label']
                    print(f"  └─ Prediction: {label}")
                else:
                    print(f"  └─ API Error: {response.status_code}")
                    
            except Exception as e:
                print(f"  └─ Connection Error: {e}")
            
            # 대기
            print(f"Waiting {INTERVAL_SECONDS} seconds...")
            time.sleep(INTERVAL_SECONDS)
            idx += 1
            
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")

if __name__ == "__main__":
    main()
