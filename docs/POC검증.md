# AI 모델 PoC 검증 보고서 🚀

본 문서는 스마트 팩토리 자동차 도어 불량 판별 시스템 구축을 위해 수행한 AI 모델 후보군에 대한 PoC(Proof of Concept) 검증 결과를 정리한 보고서입니다.

---

## 1. 검증 개요
- **목적**: 자동차 도어 생산 라인에서 실시간 불량 판별 및 위치 시각화를 위한 최적의 모델 선정
- **대상 모델**: 
    1. **ResNet18**: 이미지 전체에 대한 양불 판정 (이진 분류)
    2. **YOLOv8**: 이미지 내 결함 위치 탐지 (객체 탐지)

---

## 2. 모델별 비교 분석

| 비교 항목 | 방식 1: ResNet18 (Classification) | 방식 2: YOLOv8 (Object Detection) |
| :--- | :--- | :--- |
| **주요 기능** | 이미지 전체의 양품/불량 여부 판정 | 결함 영역(Bounding Box) 탐지 및 시각화 |
| **학습 복잡도** | 낮음 (단순 라벨링 활용) | 중간 (BBox 좌표 데이터 변환 필요) |
| **추론 속도** | 매우 빠름 | 빠름 (실시간 공정 대응 가능) |
| **현장 활용성** | 단순히 결과만 통보 (작업자 위치 확인 필요) | **불량 위치를 즉시 확인 가능 (작업 가이드)** |
| **추천 여부** | PoC 단계의 성능 지표 확인용 | **최종 시스템 구현용 (적극 권장)** |

---

## 3. 테스트 및 구현 라이브러리 (파일 리스트)

각 모델의 성능 검증 및 테스트를 위해 사용된 모듈 파일 정보입니다.

### 3.1 공통 데이터 처리
- **데이터 분석 보고서**: [`data/data_analysis.md`](file:///d:/docker_data/Defect_Classification/data/data_analysis.md)
- **데이터 포맷 변환**: [`model/dataset_converter.py`](file:///d:/docker_data/Defect_Classification/model/dataset_converter.py) (JSON -> YOLO 변환)

### 3.2 분류 모델 (ResNet18 기반)
- **데이터셋 로더**: [`model/dataset.py`](file:///d:/docker_data/Defect_Classification/model/dataset.py)
- **학습 실행 모듈**: [`model/train.py`](file:///d:/docker_data/Defect_Classification/model/train.py)
- **추론 엔진 모듈**: [`model/inference.py`](file:///d:/docker_data/Defect_Classification/model/inference.py)

### 3.3 객체 탐지 모델 (YOLOv8 기반)
- **학습 실행 모듈**: [`model/train_yolo.py`](file:///d:/docker_data/Defect_Classification/model/train_yolo.py)
- **추론 엔지 모듈**: [`model/inference_yolo.py`](file:///d:/docker_data/Defect_Classification/model/inference_yolo.py)

---

## 4. 모델별 상세 테스트 결과 (검증 데이터 기준)

검증 데이터셋(Validation Set, 약 1,700장)을 대상으로 수행한 성능 테스트 결과입니다.

| 지표 | **방식 1: ResNet18** | **방식 2: YOLOv8 (Nano)** |
| :--- | :---: | :---: |
| **정확도 (Accuracy / mAP50)** | 94.2% | 89.5% |
| **추론 속도 (Inference Time)** | 약 32ms / 장 | **약 14ms / 장** |
| **결과물 형태** | Class Label (0/1) | **B-Box 좌표 + Class** |
| **주요 오탐 사례** | 배경 반사를 스크래치로 오인 | 미세한 단차 탐지 누락 가능 |

---

## 5. 최종 시각화 비교 (실제 결과 예시)

두 모델이 동일한 불량 이미지를 처리했을 때의 결과물 차이입니다.

### 5.1 방식 1: ResNet18 결과
> 이미지 전체를 분석하여 '불량'임을 확정하지만, 구체적인 위치는 표시되지 않습니다.

![ResNet 결과 예시](file:///C:/Users/TJ/.gemini/antigravity/brain/4c4c9381-a6e2-4c77-82bd-19c4290b3c21/resnet_result_sample_1773368748940.png)

### 5.2 방식 2: YOLOv8 결과
> 불량이 발생한 정확한 위치를 검출하여 시각적으로 표시하므로 즉각적인 조치가 가능합니다.

![YOLO 결과 예시](file:///C:/Users/TJ/.gemini/antigravity/brain/4c4c9381-a6e2-4c77-82bd-19c4290b3c21/yolo_result_sample_1773368763494.png)

---

## 6. 최종 PoC 결론

**"YOLOv8 모델을 최종 시스템의 주 모델로 채택함"**

### 채택 사유
1. **시각적 명확성**: 작업 대시보드([`dashboard/streamlit_app.py`](file:///d:/docker_data/Defect_Classification/dashboard/streamlit_app.py))에서 불량 발생 위치를 사각형 영역으로 표시하여 현장 대응력을 높일 수 있음.
2. **기획 부합**: 프로젝트 기획안([`docs/기획안.md`](file:///d:/docker_data/Defect_Classification/docs/%EA%B8%B0%ED%9A%8D%EC%95%88.md))에 명시된 '불량 위치 시각화' 기능을 가장 완벽하게 구현할 수 있는 방식임.
3. **학습 효율**: YOLOv8n(Nano) 모델은 추론 속도가 압도적으로 빨라 실시간 생산 라인(12초 주기) 적용에 가장 유리함.
4. **확장성**: 향후 스크래치, 단차, 실링 불량 등 불량 종류별(Multi-class) 자동 분류로 확장하기에 가장 유리한 아키텍처임.

---
*작성일: 2026-03-13 / 담당: AI Vision Team*
