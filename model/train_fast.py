from ultralytics import YOLO

def train_yolo_fast_high_acc():

    # 모델 (초고속 Nano 모델 사용, 89% 목표)
    model = YOLO("yolov8n.pt")

    DATA_YAML = "d:/docker_data/Defect_Classification/data/yolo_dataset/dataset.yaml"

    results = model.train(
        data=DATA_YAML,

        # 학습 설정
        epochs=100,         # Nano는 빠르므로 100 에폭 설정
        imgsz=640,          # 요청하신 대로 640 유지
        batch=16,           # GPU 활용
        device=0,           # GPU 사용
        workers=4,

        # 안정적인 학습
        lr0=0.001,
        cos_lr=True,
        patience=15,

        # 데이터 증강
        mosaic=1.0,
        mixup=0.1,
        degrees=10,
        flipud=0.5,

        # 속도 최적화
        cache=True,
        amp=True,

        project="runs/detect",
        name="defect_yolo_fast_90",
        exist_ok=True
    )

    metrics = model.val()

    print("------------- RESULT -------------")
    print("mAP50:", metrics.box.map50)
    print("mAP50-95:", metrics.box.map)
    print("----------------------------------")


if __name__ == "__main__":
    train_yolo_fast_high_acc()
