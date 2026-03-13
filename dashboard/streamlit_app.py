import streamlit as st
import pandas as pd
import psycopg2
import os
import time
from datetime import datetime, timedelta

# 1. 페이지 설정 및 디자인 (밝고 깨끗한 테마 적용)
st.set_page_config(page_title="Vision AI | Smart Factory", layout="wide")

# 밝은 테마의 현대적인 UI 디자인 CSS
st.markdown("""
<style>
    /* 배경 및 기본 폰트 */
    .main { 
        background-color: #f8f9fa; 
        color: #212529; 
    }
    
    /* 카드 스타일 (밝은 배경에 그림자 효과) */
    div[data-testid="stMetric"] {
        background: #ffffff;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* 가동 상태 박스 */
    .status-container {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    .status-operating {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 2px solid #2e7d32;
    }
    .status-stopped {
        background-color: #ffebee;
        color: #c62828;
        border: 2px solid #c62828;
    }
    
    /* 타이틀 색상 보정 */
    h1, h2, h3 { color: #1a1a1b; }
    
    /* 리스트 선택 가독성 */
    .stRadio [data-testid="stMarkdownContainer"] {
        padding: 5px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# 2. DB 연결 함수
def get_db_data():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "15432"),
            database=os.getenv("DB_NAME", "defect_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASS", "1234"),
            connect_timeout=3
        )
        query = "SELECT * FROM inspection_results ORDER BY inspection_time DESC LIMIT 500"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()

# 데이터 로드
df = get_db_data()

# 3. 상태 분석
is_operating = False
if not df.empty:
    last_time = df['inspection_time'].iloc[0]
    if (datetime.now() - last_time).total_seconds() < 30:
        is_operating = True

start_time_str = "-"
elapsed_time_str = "-"
if not df.empty:
    today_data = df[df['inspection_time'].dt.date == datetime.now().date()]
    if not today_data.empty:
        start_ts = today_data['inspection_time'].min()
        start_time_str = start_ts.strftime("%H:%M:%S")
        if is_operating:
            diff = datetime.now() - start_ts
            h, r = divmod(diff.total_seconds(), 3600)
            m, s = divmod(r, 60)
            elapsed_time_str = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
        else:
            elapsed_time_str = "PAUSED"

# 4. 헤더 레이아웃
header_col1, header_col2, header_col3, header_col4 = st.columns([2.5, 1, 1, 1])

with header_col1:
    st.title("🏭 Smart Vision Dashboard")
    st.caption("AI-Powered Quality Integrity Monitoring System (Light Mode)")

with header_col2:
    s_class = "status-operating" if is_operating else "status-stopped"
    s_label = "● SYSTEM OPERATING" if is_operating else "○ SYSTEM STOPPED"
    st.markdown(f'<div class="status-container {s_class}">{s_label}</div>', unsafe_allow_html=True)

with header_col3:
    st.metric("Shift Start", start_time_str)

with header_col4:
    st.metric("Operation Time", elapsed_time_str)

st.divider()

# 5. 메인 섹션
if not df.empty:
    col_stat, col_list, col_view = st.columns([0.8, 1.2, 2])

    with col_stat:
        st.subheader("📊 Statistics")
        total = len(df)
        defects = df['is_defective'].sum()
        rate = (defects / total) * 100
        st.metric("Total Yield", f"{total} EA")
        st.metric("Total Defects", f"{defects} EA", delta=f"{defects}", delta_color="inverse")
        st.metric("Defect Rate", f"{rate:.1f}%")

    with col_list:
        st.subheader("🚨 Recent Defects")
        defects_df = df[df['is_defective'] == True].head(10).copy()
        if not defects_df.empty:
            selected_id = st.radio(
                "Select defect log to inspect:",
                options=defects_df['product_id'].unique(),
                format_func=lambda x: f"ID: {x} | {defects_df[defects_df['product_id']==x]['inspection_time'].iloc[0].strftime('%H:%M:%S')}",
                label_visibility="collapsed"
            )
            selected_row = defects_df[defects_df['product_id'] == selected_id].iloc[0]
        else:
            st.success("No defects detected in recent batch.")
            selected_row = None

    with col_view:
        st.subheader("🔍 Inspection Analysis")
        if selected_row is not None:
            # 상세 정보 요약 바
            st.markdown(f"#### ID: `{selected_row['product_id']}`")
            st.markdown(f"**Type:** {selected_row['defect_type']} | **Confidence:** {selected_row['confidence']:.2f}")
            
            res_path = selected_row['result_image_path']
            if os.path.exists(res_path):
                st.image(res_path, use_container_width=True, caption=f"Defect Localization Result ({selected_row['product_id']})")
            else:
                st.warning(f"Image data not found: {res_path}")
        else:
            st.info("Select a log from the list to view the AI analysis image.")

else:
    st.warning("No production data available. Please ensure API and Simulator are running.")

# 자동 새로고침
time.sleep(1)
if is_operating:
    st.rerun()
