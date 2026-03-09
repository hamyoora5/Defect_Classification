import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import models, transforms
from dataset import DefectDataset
from tqdm import tqdm

def train_model():
    # 1. 하이퍼파라미터 설정
    DATA_ROOT = "d:/docker_data/Defect_Classification/data/cardoor"
    BATCH_SIZE = 16
    EPOCHS = 10
    LEARNING_RATE = 0.001
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print(f"Using device: {DEVICE}")

    # 2. 데이터 전처리 정의 (ResNet 입력 규격 224x224)
    data_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # 3. 데이터셋 및 데이터로더 구성
    train_csv = os.path.join(DATA_ROOT, "train_labels.csv")
    train_img_dir = os.path.join(DATA_ROOT, "01.데이터/1.Training/원천데이터")
    train_label_dir = os.path.join(DATA_ROOT, "01.데이터/1.Training/라벨링데이터")

    train_dataset = DefectDataset(train_csv, train_img_dir, train_label_dir, transform=data_transforms)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=2)

    val_csv = os.path.join(DATA_ROOT, "validation_labels.csv")
    val_img_dir = os.path.join(DATA_ROOT, "01.데이터/2.Validation/원천데이터")
    val_label_dir = os.path.join(DATA_ROOT, "01.데이터/2.Validation/라벨링데이터")

    val_dataset = DefectDataset(val_csv, val_img_dir, val_label_dir, transform=data_transforms)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=2)

    # 4. 모델 정의 (ResNet18 기반 전이 학습)
    model = models.resnet18(pretrained=True)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 2) # 양품(0), 불량(1)
    model = model.to(DEVICE)

    # 5. 손실 함수 및 최적화 도구 설정
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 6. 학습 루프
    best_acc = 0.0
    for epoch in range(EPOCHS):
        print(f"Epoch {epoch+1}/{EPOCHS}")
        
        # Training phase
        model.train()
        running_loss = 0.0
        running_corrects = 0
        
        for batch in tqdm(train_loader):
            if batch is None: continue
            
            inputs = batch['image'].to(DEVICE)
            labels = batch['label'].to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data)
            
        epoch_loss = running_loss / len(train_dataset)
        epoch_acc = running_corrects.double() / len(train_dataset)
        print(f"Train Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}")
        
        # Validation phase
        model.eval()
        val_corrects = 0
        with torch.no_grad():
            for batch in val_loader:
                if batch is None: continue
                inputs = batch['image'].to(DEVICE)
                labels = batch['label'].to(DEVICE)
                outputs = model(inputs)
                _, preds = torch.max(outputs, 1)
                val_corrects += torch.sum(preds == labels.data)
                
        val_acc = val_corrects.double() / len(val_dataset)
        print(f"Val Acc: {val_acc:.4f}")
        
        # 모델 저장 (가장 좋은 정확도 모델)
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), "model/best_defect_model.pth")
            print(f"Best model saved with Acc: {best_acc:.4f}")

if __name__ == "__main__":
    train_model()
