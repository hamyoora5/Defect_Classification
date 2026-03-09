import os
import json
import pandas as pd
import shutil
from tqdm import tqdm

def convert_json_to_yolo():
    # 1. 경로 설정
    DATA_ROOT = "d:/docker_data/Defect_Classification/data/cardoor"
    YOLO_ROOT = "d:/docker_data/Defect_Classification/data/yolo_dataset"
    
    # 2. 카테고리 매핑 (YOLO는 0부터 시작하는 index여야 함)
    # 101: 스크래치, 204: 실링 불량 등 88개 카테고리가 있으나 PoC용으로 주요 것만 추리거나 
    # category_id 자체를 index화 함 (여기서는 단순화해서 수행)
    category_id_map = {101: 0, 102: 1, 203: 2, 204: 3} # 예시 매핑
    
    # 상위 디렉토리 생성
    for split in ['train', 'val']:
        os.makedirs(f"{YOLO_ROOT}/images/{split}", exist_ok=True)
        os.makedirs(f"{YOLO_ROOT}/labels/{split}", exist_ok=True)

    # 3. CSV 데이터 로드 및 처리 루프
    splits_info = {
        'train': os.path.join(DATA_ROOT, "train_labels.csv"),
        'val': os.path.join(DATA_ROOT, "validation_labels.csv")
    }

    for split_name, csv_path in splits_info.items():
        print(f"Processing {split_name} dataset...")
        df = pd.read_csv(csv_path)
        
        # 이미지 전체 경로 빌드 (이전 dataset.py의 로직 활용)
        img_root = f"{DATA_ROOT}/01.데이터/{'1.Training' if split_name == 'train' else '2.Validation'}/원천데이터"
        label_root = f"{DATA_ROOT}/01.데이터/{'1.Training' if split_name == 'train' else '2.Validation'}/라벨링데이터"
        
        img_path_map = {}
        label_path_map = {}
        for root, _, files in os.walk(img_root):
            for file in files: img_path_map[file] = os.path.join(root, file)
        for root, _, files in os.walk(label_root):
            for file in files: label_path_map[file] = os.path.join(root, file)

        # 개별 파일 변환
        for _, row in tqdm(df.iterrows(), total=len(df)):
            img_name = row['file_name']
            label = row['label'] # 0:양품, 1:불량
            
            # 1. 이미지 복사
            src_img = img_path_map.get(img_name)
            if not src_img: continue
            dst_img = f"{YOLO_ROOT}/images/{split_name}/{img_name}"
            shutil.copy(src_img, dst_img)
            
            # 2. 라벨 생성
            txt_name = img_name.rsplit('.', 1)[0] + '.txt'
            dst_label = f"{YOLO_ROOT}/labels/{split_name}/{txt_name}"
            
            # 양품(0)인 경우 빈 텍스트 파일 생성(No Detection)
            if label == 0:
                with open(dst_label, 'w') as f: pass
                continue
            
            # 불량인 경우 JSON에서 Bbox 추출하여 기록
            json_file = img_name.rsplit('.', 1)[0] + '.json'
            src_json = label_path_map.get(json_file)
            if not src_json:
                with open(dst_label, 'w') as f: pass
                continue
                
            with open(src_json, 'r', encoding='utf-8-sig') as f:
                ann = json.load(f)
                img_w = ann['images'][0]['width']
                img_h = ann['images'][0]['height']
                
                with open(dst_label, 'w') as lf:
                    for item in ann.get('annotations', []):
                        cat_id = item.get('category_id')
                        yolo_cat = category_id_map.get(cat_id, 0) # 기본 스크래치(0) 간주
                        
                        # YOLO format: cls, x_center, y_center, w, h (all normalized 0~1)
                        if 'bbox' in item:
                            x, y, w, h = item['bbox']
                            xc = (x + w / 2) / img_w
                            yc = (y + h / 2) / img_h
                            wn = w / img_w
                            hn = h / img_h
                            lf.write(f"{yolo_cat} {xc} {yc} {wn} {hn}\n")

    # 4. YOLO yaml 파일 생성
    yaml_content = f"""path: {YOLO_ROOT}
train: images/train
val: images/val

names:
  0: Scratch
  1: Damage
  2: Step
  3: Sealing
"""
    with open(f"{YOLO_ROOT}/dataset.yaml", 'w') as f:
        f.write(yaml_content)
    print(f"YOLO dataset conversion completed at: {YOLO_ROOT}")

if __name__ == "__main__":
    convert_json_to_yolo()
