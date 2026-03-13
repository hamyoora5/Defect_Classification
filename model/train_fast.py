from ultralytics import YOLO
import os

def train_yolo_ultra_performance():
    """
    3시간 내에 ResNet(94.2%)을 능가하는 mAP50 94%+ 달성을 위한 초고성능 학습 설정
    """
    # 1. 모델 로드 (YOLOv8n - 속도와 정확도의 최적 밸런스)
    model = YOLO('yolov8n.pt') 
    
    # 2. 데이터셋 경로
    DATA_YAML = "d:/docker_data/Defect_Classification/data/yolo_dataset/dataset.yaml"
    
    # 3. 94% 고지 점령을 위한 초강수 하이퍼파라미터
    print("🔥 Starting Ultra-Performance Training (Target: mAP50 94%+)...")
    model.train(
        data=DATA_YAML,
        epochs=50,               # 3시간 내 CPU 환경 고려, 50 에폭까지 집중 학습
        imgsz=640,               # 속도 확보를 위해 640 유지
        batch=16,                
        
        # --- 정확도 극대화 설정 ---
        lr0=0.01,                # 초기 학습률 상향 (빠른 수렴)
        lrf=0.01,                # 최종 학습률을 낮게 유지하여 정밀도 확보
        mosaic=1.0,              # 데이터 증강 극대화 (미세 결함 탐지력↑)
        mixup=0.1,               # 이미지 혼합 증강 (강인성↑)
        degrees=10,              # 회전 증강
        
        # --- 학습 관리 ---
        name='defect_yolo_fast_track', # 기존 폴더 덮어쓰기하여 API와 연동 유지
        project='runs/detect',
        exist_ok=True,
        cache=True,              # 데이터 로딩 병목 제거
        device='cpu'
    )
    
    print("✅ Ultra-Performance Training Completed! Check mAP50 in results.csv")

if __name__ == "__main__":
    train_yolo_ultra_performance()
