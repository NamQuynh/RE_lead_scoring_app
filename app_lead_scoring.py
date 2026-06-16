import streamlit as st
import pandas as pd
import os
import sys

# Đảm bảo đường dẫn import cho src/
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.data_loader import load_data_from_private_gsheet, load_data_fallback
from src.scoring import process_leads_dataframe
from src.dashboard import render_header, render_sidebar, render_kpis, render_data_table
from src.exporter import render_export_section

st.set_page_config(
    page_title="Bảng Điều Khiển Khách Hàng | AI CRM",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Hiển thị UI tĩnh
render_sidebar()
render_header()

# 2. Xử lý Dữ liệu
@st.cache_data(ttl=60)
def fetch_and_score_data():
    df_raw = load_data_from_private_gsheet()
    if df_raw is None:
        st.warning("⚠️ Không thể kết nối GSheets. Tự động chuyển sang dữ liệu dự phòng.")
        df_raw = load_data_fallback()
        
    if df_raw is not None and not df_raw.empty:
        return process_leads_dataframe(df_raw)
    return None

refresh_clicked = st.sidebar.button("🔄 Tải lại Dữ Liệu & AI")

if "scored_df" not in st.session_state or refresh_clicked:
    with st.spinner("🤖 Trợ lý AI đang tải dữ liệu và chấm điểm khách hàng..."):
        if refresh_clicked:
            fetch_and_score_data.clear()
            
        df_result = fetch_and_score_data()
        if df_result is not None:
            st.session_state.scored_df = df_result
            st.toast("AI đã nạp và phân tích dữ liệu thành công!", icon="✅")
        else:
            st.error("❌ Không có dữ liệu để xử lý.")

# 3. Hiển thị Dashboard & Chức năng
if "scored_df" in st.session_state and st.session_state.scored_df is not None:
    df_scored = st.session_state.scored_df
    
    render_kpis(df_scored)
    render_data_table(df_scored)
    render_export_section(st.session_state.scored_df)
else:
    st.info("Vui lòng cấu hình file .streamlit/secrets.toml để kết nối dữ liệu.")
