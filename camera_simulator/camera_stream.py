import os
import requests
import time
import glob
import random
from datetime import datetime

# 1. 설정 및 초기화
API_URL = os.getenv("API_URL", "http://localhost:8000/predict")
IMAGE_DIR = "d:/docker_data/Defect_Classification/data/cardoor/01.데이터/2.Validation/원천데이터"
INTERVAL_SECONDS = 12 # 기획안 기준 12초 간격

def main():
    print(f"[{datetime.now()}] Camera Simulator started.")
    print(f"Scanning for images in: {IMAGE_DIR}")
    
    # 모든 이미지 파일 경로 리스트업
    image_list = glob.glob(os.path.join(IMAGE_DIR, "**/*.jpg"), recursive=True)
    image_list += glob.glob(os.path.join(IMAGE_DIR, "**/*.jpeg"), recursive=True)
    image_list += glob.glob(os.path.join(IMAGE_DIR, "**/*.png"), recursive=True)
    
    if not image_list:
        print(f"Error: No images found in {IMAGE_DIR}")
        return

    print(f"Found {len(image_list)} images to simulate.")
    
    # 2. 시뮬레이션 루프
    try:
        while True:
            # 셔플이나 랜덤 선택 (컨베이어 벨트 흐름 모사)
            img_path = random.choice(image_list)
            file_name = os.path.basename(img_path)
            
            print(f"[{datetime.now()}] Capturing image: {file_name}")
            
            # API 전송
            try:
                with open(img_path, "rb") as f:
                    files = {"file": (file_name, f, "image/jpeg")}
                    response = requests.post(API_URL, files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  └─ Prediction: {result['prediction']['label']} (Conf: {result['prediction']['confidence']:.2f})")
                else:
                    print(f"  └─ API Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                print(f"  └─ Connection Error: API server is likely down.")
            except Exception as e:
                print(f"  └─ Error: {e}")
            
            # 12초 대기
            print(f"Waiting {INTERVAL_SECONDS} seconds for next capture...")
            time.sleep(INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\nSimulator stopped by user.")

if __name__ == "__main__":
    main()
