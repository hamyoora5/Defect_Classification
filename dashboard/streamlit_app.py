import streamlit as st
import pandas as pd
import psycopg2
import os
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="Vision AI | Smart Factory", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8f9fa; color: #212529; }
    div[data-testid="stMetric"] {
        background: #ffffff;
        padding: 15px 20px;
        border-radius: 12px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# 2. DB 연결 및 기능 함수
def get_db_data():
    try:
        conn_str = f"postgresql://postgres:1234@localhost:15432/defect_db"
        engine = create_engine(conn_str)
        query = "SELECT * FROM inspection_results WHERE inspection_time::date = CURRENT_DATE ORDER BY inspection_time DESC"
        df = pd.read_sql(query, engine)
        
        # 시간대 강제 보정 (UTC -> KST)
        if not df.empty and 'inspection_time' in df.columns:
            df['inspection_time'] = pd.to_datetime(df['inspection_time'])
            if df['inspection_time'].dt.tz is None:
                df['inspection_time'] = df['inspection_time'] + timedelta(hours=9)
            else:
                import pytz
                kst = pytz.timezone('Asia/Seoul')
                df['inspection_time'] = df['inspection_time'].dt.tz_convert(kst)
        return df
    except Exception:
        return pd.DataFrame()

def reset_production_db():
    try:
        conn = psycopg2.connect(host="localhost", port="15432", database="defect_db", user="postgres", password="1234")
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE inspection_results RESTART IDENTITY;")
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception:
        return False

# 3. 사이드바 네비게이션
with st.sidebar:
    st.header("🎮 Navigation")
    page = st.selectbox("Select Display", ["📊 Main Monitor", "🚨 Defect Analysis"])
    st.divider()
    st.header("⚙️ Admin")
    if st.button("🗑️ Reset All Data"):
        if reset_production_db():
            st.success("Database Reset!")
            time.sleep(1)
            st.rerun()

# 데이터 로드
now = datetime.now()
df = get_db_data()

# 가동 상태 판별 (마지막 데이터가 60초 이내면 Operating)
is_operating = False
current_batch_id = "N/A"
if not df.empty:
    current_batch_id = df['batch_id'].iloc[0]
    last_time = df['inspection_time'].iloc[0].replace(tzinfo=None)
    if (now - last_time).total_seconds() < 60:
        is_operating = True

# 4. 페이지 출력
if page == "📊 Main Monitor":
    # 시간 정보 계산
    start_time_str = "WAITING"
    elapsed_time_str = "00:00:00"
    if not df.empty:
        # 현재 배치 기준 필터링
        batch_df = df[df['batch_id'] == current_batch_id]
        start_ts = batch_df['inspection_time'].min().replace(tzinfo=None)
        start_time_str = start_ts.strftime("%H:%M:%S")
        
        # [핵심] 가동 중이면 현재 시각, 중단 시 마지막 데이터 시각 기준으로 스톱워치 멈춤
        ref_time = now if is_operating else df['inspection_time'].iloc[0].replace(tzinfo=None)
        delta = ref_time - start_ts
        total_sec = max(0, int(delta.total_seconds()))
        h, r = divmod(total_sec, 3600)
        m, s = divmod(r, 60)
        elapsed_time_str = f"{h:02d}:{m:02d}:{s:02d}"

    # 상단 요약 바
    h1, h2, h3, h4 = st.columns([2.2, 1, 1, 1])
    with h1:
        st.title("🏭 Production Live")
        s_color = "#2e7d32" if is_operating else "#d32f2f"
        s_bg = "#e8f5e9" if is_operating else "#ffebee"
        s_label = "● SYSTEM OPERATING" if is_operating else "○ SYSTEM STOPPED"
        st.markdown(f'<div style="padding:10px; border-radius:8px; text-align:center; font-weight:700; border:2px solid {s_color}; background-color:{s_bg}; color:{s_color};">{s_label}</div>', unsafe_allow_html=True)
    with h2: st.metric("Now (KST)", now.strftime("%H:%M:%S"))
    with h3: st.metric("Batch Start", start_time_str)
    with h4: st.metric("Running", elapsed_time_str)
    
    st.divider()

    if not df.empty:
        c1, c2, c3 = st.columns([0.8, 1.2, 2])
        with c1:
            st.subheader("📊 Monitoring")
            total_daily = len(df)
            total_defects = sum(df['is_defective'])
            
            batch_df = df[df['batch_id'] == current_batch_id]
            b_total = len(batch_df)
            b_defects = sum(batch_df['is_defective'])
            b_rate = (b_defects / b_total) * 100 if b_total > 0 else 0
            
            st.markdown("### Daily Total")
            st.metric("Total Yield", f"{total_daily} EA")
            st.metric("Total Defects", f"{total_defects} EA", delta_color="inverse")
            st.divider()
            st.markdown(f"### Batch: {current_batch_id}")
            st.metric("Batch Yield", f"{b_total} EA")
            st.metric("Batch Defects", f"{b_defects} EA", delta=f"{b_defects}", delta_color="inverse")
            st.metric("Batch Quality", f"{100-b_rate:.1f}%")
            st.progress(1.0 - (b_rate/100))
        
        with c2:
            st.subheader("🚨 Recent Logs")
            display_list = df.head(15).copy()
            selected_id = st.radio("Items", options=display_list['product_id'].tolist(),
                format_func=lambda x: f"{'🔴' if display_list[display_list['product_id']==x]['is_defective'].iloc[0] else '⚪'} ID: {x} | {display_list[display_list['product_id']==x]['inspection_time'].iloc[0].strftime('%H:%M:%S')}",
                label_visibility="collapsed")
            selected_row = display_list[display_list['product_id'] == selected_id].iloc[0]
            
        with c3:
            st.subheader("🔍 Inspection Detail")
            if selected_row is not None:
                st.markdown(f"#### PRODUCT ID: `{selected_row['product_id']}`")
                st.info(f"**Batch:** {selected_row['batch_id']} | **Time:** {selected_row['inspection_time'].strftime('%H:%M:%S')}")
                if selected_row['is_defective']: st.error(f"DEFECT: {selected_row['defect_type']}")
                else: st.success("QUALITY PASS")
                path = selected_row['result_image_path']
                if os.path.exists(path): st.image(path, use_column_width=True)
                else: st.warning("Loading analysis image...")
    else:
        st.info("Waiting for production line start...")

elif page == "🚨 Defect Analysis":
    st.title("🚨 Defect History Analysis")
    defects_only = df[df['is_defective'] == True].copy()
    if not defects_only.empty:
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.subheader("Today's Defects")
            st.dataframe(defects_only[['inspection_time', 'product_id', 'batch_id', 'defect_type']].rename(
                columns={'inspection_time': 'Time', 'product_id': 'Product ID', 'batch_id': 'Batch No', 'defect_type': 'Defect Type'}
            ), use_container_width=True, hide_index=True)
            selected_id = st.selectbox("Detailed Analysis Selection", defects_only['product_id'].tolist())
            row = defects_only[defects_only['product_id'] == selected_id].iloc[0]
        with col2:
            st.subheader("Detail View")
            st.error(f"**ID:** {row['product_id']} | **Batch:** {row['batch_id']}")
            path = row['result_image_path']
            if os.path.exists(path):
                st.image(path, use_column_width=True)
                st.json(row['bbox'])
            else: st.warning("Image not found.")
    else: st.success("No defects detected yet.")

# 자동 새로고침 (2초)
time.sleep(2)
st.rerun()
