from ultralytics import YOLO
import os

def train_yolo_poc():
    # 1. 모델 설정 (나노 모델: PoC용으로 가장 빠름)
    model = YOLO('yolov8n.pt') 
    
    # 2. 데이터셋 설정
    DATA_YAML = "d:/docker_data/Defect_Classification/data/yolo_dataset/dataset.yaml"
    
    # 3. 학습 실행
    print("Starting YOLOv8 PoC Training...")
    results = model.train(
        data=DATA_YAML,
        epochs=10,        # PoC용으로 짧게 설정
        imgsz=640,       # 이미지 사이즈
        batch=16,
        name='defect_yolo_poc'
    )
    
    # 4. 검증 및 결과 저장
    metrics = model.val()
    print(f"YOLO Training Completed. mAP50: {metrics.box.map50:.4f}")

if __name__ == "__main__":
    train_yolo_poc()
