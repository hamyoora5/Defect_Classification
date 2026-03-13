from ultralytics import YOLO
import os

def train_yolo_ultra_performance():
    """
    3시간 내에 ResNet(94.2%)을 능가하는 mAP50 94%+ 달성을 위한 초고성능 학습 설정
    """
    # 1. 모델 로드 (YOLOv8n - 속도와 정확도의 최적 밸런스)
    model = YOLO('yolov8s.pt') 
    
    # 2. 데이터셋 경로
    DATA_YAML = "d:/docker_data/Defect_Classification/data/yolo_dataset/dataset.yaml"
    
    # 3. 94% 고지 점령을 위한 최강 설정 (User Suggestion + Optimized Speed)
    print("🔥 Starting YOLOv8s Training (Target: mAP50 94%+)...")
    model.train(
        data=DATA_YAML,
        epochs=150,              # 주신 대로 150 에폭 설정
        imgsz=640,               # 주신 대로 640 해상도 (정확도 핵심)
        batch=16,                # 주신 대로 16 배치
        amp=True,                # 가속 활성화
        
        # --- 관리 설정 ---
        name='defect_yolo_v8s_final', 
        project='runs/detect',
        exist_ok=True,
        cache=True,              # 속도 보완
        device=0,
        workers=4                # 로딩 가속
    )
    
    print("✅ Ultra-Performance Training Completed! Check mAP50 in results.csv")

if __name__ == "__main__":
    train_yolo_ultra_performance()
