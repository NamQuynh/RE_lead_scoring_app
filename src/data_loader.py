import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import os

def load_data_from_private_gsheet():
    """
    Kết nối tới Private Google Sheet thông qua Service Account credentials.
    Đọc dữ liệu từ tab 'Leads' với cache (ttl).
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Sử dụng URL được cung cấp và đọc tab đầu tiên (worksheet=0) để tránh lỗi sai tên tab
        sheet_url = "https://docs.google.com/spreadsheets/d/1Og3BaCu7iSDJMLmdZJ25RfJF1qTHYSaoHXJj6UT-H6E/edit"
        df = conn.read(spreadsheet=sheet_url, worksheet=0, ttl=600)
        
        # Validate cấu trúc dữ liệu tối thiểu
        required_columns = ["lead_id", "customer_name", "phone", "email", "source", "description", "score", "segment"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            st.error(f"❌ Lỗi cấu trúc dữ liệu: Thiếu các cột bắt buộc: {', '.join(missing_cols)}")
            return None
            
        return df
    except Exception as e:
        # Silently return None on failure so caller can handle fallback
        # without causing transient UI errors.
        return None

def load_data_fallback():
    """
    Cơ chế dự phòng: Tải dữ liệu từ file Excel cục bộ khi không có mạng hoặc cấu hình lỗi.
    [DEPRECATED] Chỉ dùng cho mục đích kiểm thử.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    fallback_path = os.path.join(parent_dir, "leads_for_gsheet.xlsx")
    
    if os.path.exists(fallback_path):
        return pd.read_excel(fallback_path)
    return None

def test_connection():
    """
    Hàm kiểm tra kết nối an toàn (dùng cho debug).
    """
    st.info("🔄 Đang thử nghiệm kết nối Private Google Sheet...")
    df = load_data_from_private_gsheet()
    if df is not None:
        st.success("✅ Kết nối thành công!")
        st.write(f"- Số dòng đọc được: **{len(df)}**")
        st.write("- Các cột nhận diện được:", df.columns.tolist())
    else:
        st.warning("⚠️ Đang thử kích hoạt cơ chế dự phòng (Local Excel)...")
        df_fallback = load_data_fallback()
        if df_fallback is not None:
            st.success("✅ Đã nạp thành công từ file Excel dự phòng.")
            st.write(f"- Số dòng đọc được: **{len(df_fallback)}**")
        else:
            st.error("❌ Thất bại toàn tập: Không tìm thấy dữ liệu trên Google Sheets lẫn file dự phòng.")
