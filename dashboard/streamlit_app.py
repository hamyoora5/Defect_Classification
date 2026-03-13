import streamlit as st
import pandas as pd
import psycopg2
import os
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine

# 1. 설정 및 메타데이터
st.set_page_config(page_title="Vision AI Dashboard", layout="wide")
BATCH_FILE = "d:/docker_data/Defect_Classification/active_batch.txt"

# 2. DB 데이터 불러오기 (절대 시각 그대로)
def get_db_data():
    try:
        engine = create_engine("postgresql://postgres:1234@localhost:15432/defect_db")
        # 오늘 날짜 필터링 (컬럼이 이미 KST이므로 그대로 사용)
        query = "SELECT * FROM inspection_results WHERE inspection_time::date = CURRENT_DATE ORDER BY inspection_time DESC"
        df = pd.read_sql(query, engine)
        if not df.empty:
            df['inspection_time'] = pd.to_datetime(df['inspection_time'])
        return df
    except Exception: return pd.DataFrame()

# 3. 사이드바 (배치 입력창 상단 배치)
with st.sidebar:
    st.title("🏭 Factory Setting")
    
    # Batch ID 초기화 및 입력
    current_active_batch = "LOT-SEOUL-SAMPLE"
    if os.path.exists(BATCH_FILE):
        with open(BATCH_FILE, "r", encoding='utf-8') as f:
            current_active_batch = f.read().strip()
            
    input_id = st.text_input("📦 Current Active Batch ID", value=current_active_batch)
    if st.button("🚀 Apply New Batch ID"):
        with open(BATCH_FILE, "w", encoding='utf-8') as f:
            f.write(input_id)
        st.success(f"Applying: {input_id}")
        time.sleep(1)
        st.rerun()
        
    st.divider()
    page = st.selectbox("Display Switch", ["📊 Dashboard", "🚨 History"])
    if st.button("🗑️ Reset ALL Data"):
        conn = psycopg2.connect(host="localhost", port="15432", database="defect_db", user="postgres", password="1234")
        cur = conn.cursor()
        cur.execute("TRUNCATE TABLE inspection_results RESTART IDENTITY;")
        conn.commit()
        conn.close()
        st.rerun()

# 4. 공통 데이터 계산
# 서울 현재 시각 (기준값)
now_kst = datetime.now(timezone(timedelta(hours=9))).replace(tzinfo=None)
df = get_db_data()

is_operating = False
display_batch_id = input_id
batch_df = pd.DataFrame()

if not df.empty:
    display_batch_id = df['batch_id'].iloc[0]
    batch_df = df[df['batch_id'] == display_batch_id].copy()
    
    # 가동 판별 (최근 65초)
    last_val = df['inspection_time'].iloc[0].replace(tzinfo=None)
    if (now_kst - last_val).total_seconds() < 65:
        is_operating = True

# 5. UI 렌더링
if page == "📊 Dashboard":
    # Runtime (STOP 기능 강화)
    start_time_str = "WAITING"
    elapsed_time_str = "00:00:00"
    if not batch_df.empty:
        start_ts = batch_df['inspection_time'].min().replace(tzinfo=None)
        start_time_str = start_ts.strftime("%H:%M:%S")
        # [핵심] 멈추면 마지막 데이터 시각 기준으로 스톱!
        ref = now_kst if is_operating else batch_df['inspection_time'].max().replace(tzinfo=None)
        delta = ref - start_ts
        total_sec = max(0, int(delta.total_seconds()))
        h, r = divmod(total_sec, 3600)
        m, s = divmod(r, 60)
        elapsed_time_str = f"{h:02d}:{m:02d}:{s:02d}"

    # 상단 요약
    st.title("🏭 Production Live Monitor")
    st.divider()
    
    h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
    with h1:
        color = "#2e7d32" if is_operating else "#d32f2f"
        label = "SYSTEM OPERATING" if is_operating else "SYSTEM STOPPED"
        st.markdown(f'''<div style="background:{color}; color:white; padding:15px; border-radius:10px; text-align:center; font-size:24px; font-weight:bold;">● {label}</div>''', unsafe_allow_html=True)
    with h2: st.metric("Local Seoul Time", now_kst.strftime("%H:%M:%S"))
    with h3: st.metric("Current Batch Start", start_time_str)
    with h4: st.metric("Actual Runtime", elapsed_time_str)

    st.divider()
    
    # 메인 지표
    if not df.empty:
        stat_c, log_c, img_c = st.columns([0.8, 1.2, 2])
        with stat_c:
            st.subheader("Daily Stats")
            st.metric("Total Daily", f"{len(df)} EA")
            st.divider()
            st.markdown(f"#### Active Batch: {display_batch_id}")
            b_total = len(batch_df)
            b_defects = sum(batch_df['is_defective'])
            st.metric("Yield", f"{b_total} EA")
            st.metric("Defects", f"{b_defects} EA", delta=f"{b_defects}", delta_color="inverse")
        with log_c:
            st.subheader("Live Logs")
            view_df = df.head(15).copy()
            selected_id = st.radio("Items", options=view_df['product_id'].tolist(),
                format_func=lambda x: f"{'🔴' if view_df[view_df['product_id']==x]['is_defective'].iloc[0] else '⚪'} ID: {x} | {view_df[view_df['product_id']==x]['inspection_time'].iloc[0].strftime('%H:%M:%S')}",
                label_visibility="collapsed")
            row = view_df[view_df['product_id'] == selected_id].iloc[0]
        with img_c:
            st.subheader("Deep Learning Result")
            st.write(f"**ID:** {row['product_id']} | **Recorded:** {row['inspection_time'].strftime('%H:%M:%S')}")
            if row['is_defective']: st.error(f"DETECTION: {row['defect_type']}")
            else: st.success("DETECTION: PASS")
            if os.path.exists(row['result_image_path']): st.image(row['result_image_path'], use_column_width=True)
    else: st.info("Waiting for first inspection signal...")

elif page == "🚨 History":
    st.title("🚨 Detailed Defect History")
    defects = df[df['is_defective'] == True].copy()
    if not defects.empty:
        st.dataframe(defects[['inspection_time', 'product_id', 'batch_id', 'defect_type']].rename(
            columns={'inspection_time': 'Time', 'product_id': 'ID', 'batch_id': 'Batch', 'defect_type': 'Type'}
        ), use_container_width=True, hide_index=True)
    else: st.success("Perfect Quality! No defects today.")

# 자동 새로고침
time.sleep(2)
st.rerun()
