import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
import numpy as np

class DefectInference:
    """
    자동차 도어 이미지 불량 판별 및 시각화용 추론 클래스
    """
    def __init__(self, model_path, device=None):
        self.device = device if device else torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path)
        self.model.eval()
        
        # ResNet용 전처리 정의
        self.preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
    def _load_model(self, model_path):
        model = models.resnet18()
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, 2)
        
        try:
            # state_dict 로딩 시도
            state_dict = torch.load(model_path, map_location=self.device)
            if isinstance(state_dict, dict):
                model.load_state_dict(state_dict)
            else:
                model = state_dict # Model object 자체일 경우
        except Exception as e:
            print(f"Model load error: {e}. Starting with untrained model.")
            
        return model.to(self.device)

    def predict(self, image_path):
        """
        이미지 경로를 하나 받아서 예측 결과를 반환함
        """
        # 이미지 로딩
        image = Image.open(image_path).convert('RGB')
        input_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
        
        # 추론
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, preds = torch.max(probabilities, 1)
            
        label_idx = preds.item()
        label_name = "양품" if label_idx == 0 else "불량품"
        conf_val = confidence.item()
        
        return {
            "is_defective": bool(label_idx),
            "label": label_name,
            "confidence": conf_val,
            "defect_type": "스크래치" if label_idx == 1 else None # 예시용
        }

    def draw_bbox(self, image_path, bboxes, output_path):
        """
        이미지에 Bbox를 그려서 저장 (OpenCV 활용)
        bboxes (list): [[x, y, w, h], ...]
        """
        img = cv2.imread(image_path)
        for bbox in bboxes:
            x, y, w, h = map(int, bbox)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 3) # RED
            cv2.putText(img, "Defect", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            
        cv2.imwrite(output_path, img)
        return output_path

if __name__ == "__main__":
    # 추론 테스트 코드
    MODEL_PATH = "d:/docker_data/Defect_Classification/data/cardoor/model/resnet_binary_model.pth"
    TEST_IMAGE = "d:/docker_data/Defect_Classification/data/cardoor/01.데이터/1.Training/원천데이터/도어/스크래치/204_101_20_00a36e27-6f63-4965-bb71-9312f03d9db6.jpg"
    
    inference = DefectInference(MODEL_PATH)
    result = inference.predict(TEST_IMAGE)
    print(f"Prediction result: {result}")
