from ultralytics import YOLO
import cv2
import os

class YOLOInference:
    """
    YOLOv8 기반 불량 탐지 전용 추론 클래스
    """
    def __init__(self, model_path):
        # 1. 모델 로드 (가장 최근에 학습된 best.pt 사용 예정)
        self.model = YOLO(model_path)
        
    def predict(self, image_path, save=True, output_path="results/"):
        # 2. 추론 수행
        results = self.model.predict(
            source=image_path,
            save=save,
            project=output_path, 
            name='inference_result',
            conf=0.25 # 기본 신뢰도 임계값
        )
        
        # 3. 결과 파싱 (첫 번째 결과물 기준)
        res = results[0]
        boxes = res.boxes
        
        # 결과 이미지 경로 (ultralytics가 자동 생성한 경로 반환)
        res_img_path = os.path.join(res.save_dir, os.path.basename(image_path))
        
        detections = []
        for box in boxes:
            detections.append({
                "class": int(box.cls),
                "conf": float(box.conf),
                "bbox": [float(x) for x in box.xyxy[0]] # [x1, y1, x2, y2]
            })
            
        print(f"YOLO Detect {len(detections)} defects in {image_path}")
        return {
            "is_defective": len(detections) > 0,
            "detections": detections,
            "result_image": res_img_path
        }

if __name__ == "__main__":
    # YOLO 추론 테스트 코드 (학습 결과물이 있을 때 실행 가능)
    # weights_path = "runs/detect/defect_yolo_poc/weights/best.pt"
    # if os.path.exists(weights_path):
    #     yolo = YOLOInference(weights_path)
    #     yolo.predict("test.jpg")
    pass
