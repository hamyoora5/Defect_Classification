# Smart Factory Vision AI 🚗

자동차 생산 라인에서 **자동차 도어 이미지를 실시간 분석하여 불량 여부를 판별**하고 결함 위치를 추적하는 AI 비전 시스템입니다.
본 시스템은 **초고속 이진 분류(ResNet)**와 **정밀 결함 탐지(YOLO)**를 결합한 **2-Stage 파이프라인**을 통해 대규모 이미지 처리의 효율성과 탐지 정확도를 동시에 확보합니다.

---

## 1. 프로젝트 개요

### 1.1 배경 및 목적
자동차 제조 공정의 품질 검사는 높은 정밀도와 실시간성을 요구합니다. 기존의 인력 중심 검사 방식의 한계를 극복하기 위해, 본 프로젝트는 다음과 같은 목표를 가집니다.
- **실시간 탐지**: 생산 라인의 흐름을 방해하지 않는 고속 분석.
- **정밀 시각화**: 결함의 종류(스크래치, 손상 등)와 위치를 정확히 표시.
- **데이터 기반 관리**: 검사 결과를 데이터베이스화하여 품질 관리 고도화.

---

## 2. 생산 라인 사양 및 설계 근거

본 시스템은 실제 자동차 생산 환경을 가정한 시나리오를 바탕으로 설계되었습니다.

### 2.1 도어 규격 및 속도
- **자동차 도어 평균 규격**: 약 1.2 m × 1.0 m
- **컨베이어 벨트 속도**: 약 3 m/min ~ 6 m/min (0.05 m/s ~ 0.1 m/s)
- **검사 구간 통과 시간**: 약 12~24초

### 2.2 15초 주기 분석 설정의 근거
하나의 도어가 검사 구간을 통과하는 최소 시간(12초)과 최대 시간(24초)을 고려하여, **15초마다 이미지 촬영 및 전송**이 이루어지도록 시스템을 설계하였습니다.

---

## 3. 시스템 아키텍처

```
[Camera / Image Capture]
        │
        │ 15초마다 이미지 생성
        ▼
[Camera Simulator]
        │
        ▼
[AI Inference Pipeline (2-Stage)]
        │
        ├─ 1. ResNet Binary Classifier (양품/불량 분류)
        │       │
        │       └─ [If Defect]
        │             ▼
        └─ 2. YOLO Detector (결함 위치 탐지)
        │
        ▼
[FastAPI Server]
        │
        ├ 결과 저장 (이미지 경로, 불량 좌표, 신뢰도)
        │
        ▼
[PostgreSQL Database]
        │
        ▼
[Streamlit Dashboard]
        │
        ▼
[실시간 생산 및 품질 모니터링]
```

---

## 4. 기술 스택 (Tech Stack)

### 4.1 AI Training & Modeling
- **Hardware**: Google Colab T4 GPU
- **Framework**: PyTorch, Ultralytics (YOLOv8)
- **Library**: OpenCV, Pandas, Pillow
- **Optimization**: imgsz=1024, High-Res Training

### 4.2 System Interface
- **Backend**: FastAPI
- **Dashboard**: Streamlit
- **Database**: PostgreSQL
- **Infrastructure**: Docker Desktop (PostgreSQL)

---

## 5. 데이터 전처리 상세 (JSON to YOLO)

### 5.1 데이터 병합 및 해제
- **Tar 병합**: 외부 분할 압축 파일(`.tar.partX`)을 Windows `copy /b` 명령어로 병합합니다.
- **파일 매칭**: CSV 로그를 기반으로 원천 이미지와 JSON 라벨 데이터를 1:1 매칭합니다.

### 5.2 YOLO 좌표 정규화 수식
JSON 내의 절대 좌표(`[x, y, width, height]`)를 YOLO의 상대 좌표(`[class, x_center, y_center, w, h]`)로 변환합니다.
- `x_center = (x + width / 2) / Image_Width`
- `y_center = (y + height / 2) / Image_Height`
- `w = width / Image_Width`, `h = height / Image_Height`

---

## 6. AI 모델 사양

| 단계 | 모델 | 목적 | 모델 파일 경로 |
| :--- | :--- | :--- | :--- |
| **1단** | **ResNet-18 (Binary)** | 고속 양품/불량 이진 판별 | `model/resnet_binary_model.pth` |
| **2단** | **YOLOv8s** | 결함 위치 정밀 탐지 | `runs/detect/best.pt` |

---

## 7. 프로젝트 구조 및 실행 방법

### 7.1 디렉토리 구조 및 핵심 파일
```text
smart-factory-vision-ai
├─ model/
│  ├─ dataset_converter.py    # JSON 라벨을 YOLO 포맷(.txt)으로 변환
│  ├─ train_yolo_final.py     # Google Colab T4 최적화 YOLO 학습 스크립트
│  ├─ integrated_inference.py # ResNet(1단) + YOLO(2단) 통합 추론 로직
│  ├─ resnet_binary_model.pth # 1단계 양품/불량 판별용 사전 학습 모델
│  └─ inference_yolo.py       # YOLO 단독 테스트 및 추론용 스크립트
│
├─ api/
│  └─ fastapi_server.py       # 추론 요청 수신 및 2단계 파이프라인 실행 서버
│
├─ dashboard/
│  └─ streamlit_app.py        # 검사 결과 및 결함 위치 실시간 시각화 대시보드
│
├─ camera_simulator/
│  └─ camera_stream.py        # 15초 주기로 고해상도 이미지를 서버로 전송 시뮬레이션
│
├─ database/
│  ├─ schema.sql              # PostgreSQL 테이블 설계 (결함 좌표, 신뢰도 등)
│  └─ db_init.py              # 데이터베이스 구성 및 초기화 스크립트
│
├─ data/
│  └─ yolo_dataset/           # 변환이 완료된 YOLO 표준 학습 데이터셋
│
├─ docker-compose.yml         # PostgreSQL 데이터베이스 인프라 구성 (Docker)
└─ requirements.txt           # 프로젝트 실행을 위한 라이브러리 목록
```

### 7.2 실행 가이드
1. **인프라 시작**: `docker-compose up -d`
2. **DB 초기화**: `python database/db_init.py`
3. **서버 구동**: `python api/fastapi_server.py`
4. **대시보드 시작**: `streamlit run dashboard/streamlit_app.py`
5. **시뮬레이션**: `python camera_simulator/camera_stream.py`

---
*본 프로젝트는 스마트 팩토리의 불량 비전 검사 시스템 실무 PoC를 목표로 합니다.*
