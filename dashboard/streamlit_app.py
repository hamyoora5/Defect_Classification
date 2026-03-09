import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="Vision AI Dashboard", layout="wide")

# 1. DB 연결 함수
def get_db_data():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "15432"),
            database=os.getenv("DB_NAME", "defect_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "1234")
        )
        query = "SELECT * FROM inspection_results ORDER BY inspection_time DESC LIMIT 1000"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        # 테스트용 더미 데이터 반환 (DB 없을 시 대비)
        return pd.DataFrame({
            'inspection_time': [datetime.now() - timedelta(minutes=i*10) for i in range(10)],
            'is_defective': [True, False, False, True, False, False, False, True, False, False],
            'confidence': [0.95, 0.99, 0.98, 0.92, 0.97, 0.99, 0.99, 0.88, 0.99, 0.99],
            'label': ['불량품', '양품', '양품', '불량품', '양품', '양품', '양품', '불량품', '양품', '양품'],
            'product_id': [f'PART_{i}' for i in range(10)]
        })

# 2. 메인 페이지 구성
st.title("🚗 Smart Factory Vision AI Dashboard")
st.subheader("실시간 자동차 도어 생산 품질 모니터링")

# 데이터 로드
df = get_db_data()

# 3. 상단 메트릭 (KPI)
if not df.empty:
    total_count = len(df)
    defect_count = df['is_defective'].sum()
    defect_rate = (defect_count / total_count) * 100 if total_count > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("총 생산량 (Recent 1000)", f"{total_count} EA")
    col2.metric("불량 검출수", f"{defect_count} EA", delta_color="inverse")
    col3.metric("평균 불량률", f"{defect_rate:.2f}%", delta=f"{defect_rate - 5:.1f}%" if defect_rate > 5 else None, delta_color="inverse")

# 4. 차트 및 상세 데이터
st.divider()
col_left, col_right = st.columns([2, 1])

with col_left:
    st.write("### 📈 시간대별 불량 발생 현황")
    if not df.empty:
        df['hour'] = pd.to_datetime(df['inspection_time']).dt.floor('H')
        hourly_stats = df.groupby('hour').agg({'is_defective': 'sum', 'product_id': 'count'}).rename(columns={'product_id': 'total'})
        st.line_chart(hourly_stats['is_defective'])

with col_right:
    st.write("### 🚨 최근 불량 항목 리스트")
    if not df.empty:
        recent_defects = df[df['is_defective'] == True].head(5)
        st.dataframe(recent_defects[['product_id', 'confidence', 'inspection_time']])

# 5. 상세 데이터 테이블
st.write("### 📋 전체 생산 이력 (최근 100건)")
st.dataframe(df.head(100), use_container_width=True)

# 자동 새로고침 (옵션)
if st.button('데이터 수동 새로고침'):
    st.rerun()
