from ultralytics import YOLO
import cv2
import os
import torch

class YOLOInference:
    """
    YOLOv8 기반 불량 탐지 전용 추론 클래스 (CPU/GPU 지원)
    """
    def __init__(self, model_path, device=None):
        # 1. 디바이스 설정 (기본적으로 가속기 없으면 CPU)
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        print(f"Initializing YOLO Model on device: {self.device}")
        
        # 2. 모델 로드
        if not os.path.exists(model_path):
            print(f"Warning: Model file not found at {model_path}. Using base yolov8n.pt for initialization.")
            self.model = YOLO('yolov8n.pt')
        else:
            self.model = YOLO(model_path)
            
        self.model.to(self.device)
        
    def predict(self, image_path, save=True, output_path="runs/inference/"):
        """
        이미지에서 결함을 탐지하고 결과를 반환합니다.
        """
        # 3. 추론 수행
        results = self.model.predict(
            source=image_path,
            save=save,
            project=output_path, 
            name='latest',
            exist_ok=True,
            conf=0.25,
            device=self.device
        )
        
        # 4. 결과 파싱
        res = results[0]
        boxes = res.boxes
        
        # 결과 이미지 경로 (ultralytics가 저장한 경로)
        # save=True일 경우 project/name 경로에 저장됨
        filename = os.path.basename(image_path)
        res_img_path = os.path.join(output_path, 'latest', filename)
        
        detections = []
        for box in boxes:
            cls_id = int(box.cls)
            class_name = self.model.names[cls_id]
            detections.append({
                "class_id": cls_id,
                "label": class_name,
                "confidence": float(box.conf),
                "bbox": [float(x) for x in box.xyxy[0]] # [x1, y1, x2, y2]
            })
            
        return {
            "is_defective": len(detections) > 0,
            "label": "불량" if len(detections) > 0 else "양품",
            "confidence": float(boxes.conf[0]) if len(detections) > 0 else 0.0,
            "defect_type": detections[0]['label'] if len(detections) > 0 else None,
            "detections": detections,
            "result_image": res_img_path.replace("\\", "/")
        }

if __name__ == "__main__":
    # 간단한 연동 테스트 (CPU 강제)
    model_file = "runs/detect/defect_yolo_final_optimized/weights/last.pt"
    inference = YOLOInference(model_file, device='cpu')
    print("YOLO Inference class ready.")
