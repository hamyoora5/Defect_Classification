-- Smart Factory Vision AI Database Schema
-- PostgreSQL 기준

-- 1. 검사 결과 테이블 생성
CREATE TABLE IF NOT EXISTS inspection_results (
    id SERIAL PRIMARY KEY,              -- PK
    product_id VARCHAR(50) NOT NULL,    -- 제품 고유 ID (파일명 등)
    image_path TEXT NOT NULL,           -- 원본 이미지 저장 경로
    result_image_path TEXT,            -- Bbox가 그려진 결과 이미지 경로
    inspection_time TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, -- 검사 시간 (타임존 포함)
    quality VARCHAR(10) NOT NULL,       -- 판별 결과 ('양품', '불량품')
    is_defective BOOLEAN NOT NULL,      -- 불량 여부 (True: 불량, False: 양품)
    confidence FLOAT,                   -- 모델의 예측 신뢰도 (0.0 ~ 1.0)
    defect_type VARCHAR(50),            -- 불량 종류 (스크래치, 단차 등)
    bbox JSONB                          -- 불량 위치 좌표 (x, y, w, h) - JSONB 타입 활용
);

-- 2. 인덱스 생성 (조회 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_inspection_time ON inspection_results(inspection_time);
CREATE INDEX IF NOT EXISTS idx_is_defective ON inspection_results(is_defective);
CREATE INDEX IF NOT EXISTS idx_product_id ON inspection_results(product_id);

-- 3. 샘플 데이터 (테스트용)
-- INSERT INTO inspection_results (product_id, image_path, result_image_path, quality, is_defective, confidence, defect_type, bbox)
-- VALUES ('204_101_10_0a0a37bd', '/data/img/test.jpg', '/data/result/test_res.jpg', '불량품', TRUE, 0.95, '스크래치', '[{"x": 100, "y": 200, "w": 50, "h": 50}]');
