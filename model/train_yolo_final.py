from ultralytics import YOLO
import os

def train_yolo_final_optimized():
    """
    YOLOv8n 모델의 속도는 유지하면서 정확도를 최대화한 최종 최적화 학습 스크립트
    """
    # 1. 모델 로드 (Nano 모델 사용 - 속도 최적화)
    model = YOLO('yolov8n.pt') 
    
    # 2. 데이터셋 경로 설정
    DATA_YAML = "d:/docker_data/Defect_Classification/data/yolo_dataset/dataset.yaml"
    
    # 3. 최적화된 하이퍼파라미터로 학습 실행
    print("Starting Optimized YOLOv8 Training for Maximum Accuracy...")
    results = model.train(
        data=DATA_YAML,
        epochs=100,              # 충분한 학습 횟수 확보
        patience=20,             # 20 epoch 동안 성능 향상 없으면 조기 종료 (과적합 방지)
        imgsz=1024,              # 이미지 해상도 상향 (미세 결함 탐지력 강화)
        batch=8,                 # 메모리 사용량과 학습 안정성 고려 (고해상도이므로 8~16 추천)
        
        # --- 하이퍼파라미터 최적화 ---
        lr0=0.01,                # 초기 학습률
        lrf=0.01,                # 최종 학습률 비율
        momentum=0.937,          # 모멘텀
        weight_decay=0.0005,     # 가중치 감쇠
        
        # --- 데이터 증강 (Augmentation) 강화 ---
        mosaic=1.0,              # 4장의 이미지를 합쳐 학습 (배경 노이즈 강인성)
        mixup=0.1,               # 이미지 혼합 증강 적용
        degrees=15,              # 이미지 회전 허용 (현장 카메라 각도 고려)
        flipud=0.5,              # 상하 반전 허용
        
        # --- 프로젝트 관리 ---
        name='defect_yolo_final_optimized',
        project='runs/detect',
        exist_ok=True,
        cache=True               # 학습 속도 향상을 위한 데이터 캐싱
    )
    
    # 4. 검증 성능 리포트
    metrics = model.val()
    print("-" * 30)
    print(f"Final Optimized mAP50: {metrics.box.map50:.4f}")
    print(f"Final Optimized mAP50-95: {metrics.box.map:.4f}")
    print("Best Model Path: runs/detect/defect_yolo_final_optimized/weights/best.pt")
    print("-" * 30)

if __name__ == "__main__":
    train_yolo_final_optimized()
