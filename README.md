# Smart Factory Vision AI 🚗

자동차 생산 라인에서 **자동차 도어의 이미지를 실시간으로 분석하여 불량 여부를 판별**하고 시각화하는 AI 비전 시스템입니다.

## 📁 프로젝트 구조

```text
smart-factory-vision-ai
│
├─ camera_simulator (12초 간격 이미지 캡처 시뮬레이션)
│   └─ camera_stream.py
│
├─ model (AI 모델 학습, 데이터 로더 및 추론 엔진)
│   ├─ dataset.py
│   ├─ train.py
│   └─ inference.py
│
├─ api (FastAPI 기반 결과 수신 및 추론 서비스)
│   └─ fastapi_server.py
│
├─ dashboard (Streamlit 기반 생산 품질 모니터링)
│   └─ streamlit_app.py
│
├─ database (PostgreSQL 스키마 및 초기화 스크립트)
│   ├─ schema.sql
│   └─ db_init.py
│
└─ docker-compose.yml (데이터베이스 인프라 구성)
```

## 🚀 실행 가이드

### 1. 데이터베이스 서버 실행 (Docker)
먼저 PostgreSQL 서비스를 시작합니다.
```bash
docker-compose up -d
```

### 2. 패키지 설치
필요한 라이브러리를 설치합니다.
```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 초기화
테이블 스키마를 생성합니다. (PostgreSQL 컨테이너 실행 확인 필수)
```bash
python database/db_init.py
```

### 4. API 서버 실행 (Inference Server)
AI 모델을 로드하여 대기합니다.
```bash
python api/fastapi_server.py
```

### 5. 대시보드 실행 (Quality Dashboard)
브라우저에서 생산 현황을 확인합니다.
```bash
streamlit run dashboard/streamlit_app.py
```

### 6. 카메라 시뮬레이터 실행 (Simulation)
12초 간격으로 이미지를 캡처하여 검사를 요청합니다.
```bash
python camera_simulator/camera_stream.py
```

---
*본 프로젝트는 스마트 팩토리 환경의 비전 검사 시스템 PoC를 위해 설계되었습니다.*
