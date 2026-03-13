import os
import glob
import pandas as pd
import random

def generate_shuffled_validation_csv():
    img_dir = "d:/docker_data/Defect_Classification/data/yolo_dataset/images/val"
    files = glob.glob(os.path.join(img_dir, "*.*"))
    
    # 정상과 불량 분류
    normals = [f for f in files if "_10_" in os.path.basename(f)]
    defects = [f for f in files if "_10_" not in os.path.basename(f)]
    
    # 리스트 섞기
    random.shuffle(normals)
    random.shuffle(defects)
    
    # 섞어서 합치기 (정상 3개당 불량 1개 비율로 섞기)
    mixed_list = []
    n_idx, d_idx = 0, 0
    
    while n_idx < len(normals) or d_idx < len(defects):
        # 정상 3개 넣기
        for _ in range(3):
            if n_idx < len(normals):
                mixed_list.append(normals[n_idx])
                n_idx += 1
        # 불량 1개 넣기
        if d_idx < len(defects):
            mixed_list.append(defects[d_idx])
            d_idx += 1
            
    # 데이터프레임 생성
    data = []
    for f in mixed_list:
        fname = os.path.basename(f)
        data.append({
            "product_id": fname,
            "is_defective": "_10_" not in fname
        })
    
    df = pd.DataFrame(data)
    df.to_csv("d:/docker_data/Defect_Classification/validation_defects_list.csv", index=False, encoding='utf-8-sig')
    print(f"Mixed CSV generated: {len(df)} items (Normals and Defects mixed).")

if __name__ == "__main__":
    generate_shuffled_validation_csv()
