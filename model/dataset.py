import os
import json
import torch
import cv2
import pandas as pd
from torch.utils.data import Dataset
from PIL import Image

class DefectDataset(Dataset):
    """
    자동차 도어 불량 판별 데이터셋 클래스 (PyTorch)
    
    Attributes:
        csv_file (str): 이미지 파일명과 라벨(0, 1)이 포함된 CSV 파일 경로
        img_dir (str): 원천데이터(이미지) 상위 디렉토리
        label_dir (str): 라벨링데이터(JSON) 상위 디렉토리
        transform (callable): 이미지 전처리/증강용 transform
    """
    def __init__(self, csv_file, img_dir, label_dir, transform=None):
        self.data_info = pd.read_csv(csv_file)
        self.img_dir = img_dir
        self.label_dir = label_dir
        self.transform = transform
        
        # 파일명 -> 전체 경로 매핑 빌드 (OS 횡단 검색 방지용)
        self.img_path_map = self._build_path_map(img_dir, ['.jpg', '.jpeg', '.JPG'])
        self.label_path_map = self._build_path_map(label_dir, ['.json'])
        
        # 실제 존재하는 이미지 파일만 남김 (전처리)
        initial_len = len(self.data_info)
        self.data_info = self.data_info[self.data_info.iloc[:, 0].isin(self.img_path_map.keys())].reset_index(drop=True)
        print(f"Dataset Filtered: {len(self.data_info)}/{initial_len} samples remain.")

    def _build_path_map(self, root_dir, extensions):
        path_map = {}
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    path_map[file] = os.path.join(root, file)
        return path_map

    def __len__(self):
        return len(self.data_info)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        img_name = self.data_info.iloc[idx, 0]
        label = self.data_info.iloc[idx, 5]  # CSV의 'label' 컬럼 (0: 양품, 1: 불량)
        
        # 이미지 경로 확인
        img_path = self.img_path_map.get(img_name)
        if not img_path:
            return None # 혹은 에러 처리
            
        # 이미지 로딩
        image = Image.open(img_path).convert('RGB')
        
        # JSON 데이터 로딩 (필요시 Bbox 정보 등 추출)
        label_file = img_name.rsplit('.', 1)[0] + '.json'
        label_path = self.label_path_map.get(label_file)
        
        bboxes = []
        if label_path:
            with open(label_path, 'r', encoding='utf-8-sig') as f:
                ann = json.load(f)
                # annotations에서 Bbox 정보 추출
                for item in ann.get('annotations', []):
                    if 'bbox' in item:
                        bboxes.append(item['bbox']) # [x, y, w, h] format
        
        if self.transform:
            image = self.transform(image)

        # 샘플 구성
        sample = {
            'image': image,
            'label': torch.tensor(label, dtype=torch.long),
            # 'bboxes': torch.tensor(bboxes, dtype=torch.float32) if bboxes else torch.zeros((0, 4)),
            'file_name': img_name
        }

        return sample

if __name__ == "__main__":
    # 데이터셋 테스트 코드
    DATA_ROOT = "d:/docker_data/Defect_Classification/data/cardoor"
    train_csv = os.path.join(DATA_ROOT, "train_labels.csv")
    train_img_dir = os.path.join(DATA_ROOT, "01.데이터/1.Training/원천데이터")
    train_label_dir = os.path.join(DATA_ROOT, "01.데이터/1.Training/라벨링데이터")
    
    dataset = DefectDataset(train_csv, train_img_dir, train_label_dir)
    print(f"Total dataset size: {len(dataset)}")
    
    # 첫 번째 데이터 확인
    sample = dataset[0]
    if sample:
        print(f"Sample file: {sample['file_name']}")
        print(f"Label: {sample['label']}")
        print(f"Bboxes shape: {sample['bboxes'].shape}")
    else:
        print("Data loading failed.")
