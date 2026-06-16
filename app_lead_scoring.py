import streamlit as st
import pandas as pd
import os
import sys
import io

# Định nghĩa Font và Google Fonts cho ứng dụng
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Để có thể chạy cả độc lập (Self-contained) hoặc trong Workspace
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import an toàn lõi AI Lead Scoring (trong cùng thư mục hoặc fallback)
try:
    from ai_scoring_engine import process_leads_dataframe
except ImportError:
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.join(workspace_root, "03_cong_cu"))
    from ai_scoring_engine import process_leads_dataframe

# Cấu hình đường dẫn file Excel cục bộ dự phòng
LOCAL_FILE_PATH = os.path.join(current_dir, "leads_for_gsheet.xlsx")

if not os.path.exists(LOCAL_FILE_PATH):
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOCAL_FILE_PATH = os.path.join(workspace_root, "01_dau_vao", "buoi_07", "leads_for_gsheet.xlsx")

st.set_page_config(
    page_title="Bảng Điều Khiển Khách Hàng | Bất Động Sản",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Thuần Việt & Tối ưu Giao diện)
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1, h2, h3 { font-family: 'Outfit', sans-serif; }
    div, p, span { font-family: 'Inter', sans-serif; }
    
    .header-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
        border-left: 6px solid #3b82f6;
    }
    .header-title { font-size: 2.2rem; font-weight: 800; margin: 0 0 10px 0; }
    .header-subtitle { font-size: 1.05rem; color: #94a3b8; margin: 0; font-weight: 400; }
    
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(226, 232, 240, 0.8);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
    div[data-testid="stMetricValue"] { font-size: 2.4rem; font-weight: 800; }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem; font-weight: 600; color: #64748b; }
    
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 12px 28px !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .stButton>button:hover { transform: translateY(-2px) !important; }
    .stAlert { border-radius: 12px !important; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h2 style='margin: 0; color: #1e293b; font-family: Outfit; font-weight: 800;'>🏡 Trợ Lý AI BĐS</h2>
        <p style='color: #64748b; font-size: 0.85rem; margin-top: 5px;'>Hệ Thống Phân Bổ Khách Hàng</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.divider()

st.sidebar.subheader("🔌 Cấu Hình Nguồn Dữ Liệu")
data_source = st.sidebar.radio(
    "Chọn phương thức nạp dữ liệu:",
    ("📁 Dùng file Excel cục bộ", "🌐 Kết nối Google Sheets")
)

st.sidebar.divider()

df_raw = pd.DataFrame()
load_status = ""

if data_source == "📁 Dùng file Excel cục bộ":
    if os.path.exists(LOCAL_FILE_PATH):
        try:
            df_raw = pd.read_excel(LOCAL_FILE_PATH)
            load_status = "local_success"
        except Exception as e:
            st.sidebar.error(f"Lỗi đọc file Excel cục bộ: {e}")
    else:
        st.sidebar.error(f"Không tìm thấy file Excel cục bộ tại: {LOCAL_FILE_PATH}")
else:
    st.sidebar.markdown("**Mẫu liên kết Google Sheet:**")
    st.sidebar.code("https://docs.google.com/spreadsheets/d/your-id/edit")
    gsheet_url = st.sidebar.text_input("Dán liên kết Google Sheet:", key="gsheet_url_input")
    
    sheet_type = st.sidebar.selectbox("Chế độ truy cập:", ("Trang tính Công khai", "Trang tính Nội bộ bảo mật"))
    
    if gsheet_url:
        try:
            if sheet_type == "Trang tính Công khai":
                if "/edit" in gsheet_url:
                    export_url = gsheet_url.split("/edit")[0] + "/export?format=xlsx"
                else:
                    export_url = gsheet_url
                df_raw = pd.read_excel(export_url)
                load_status = "gsheet_public_success"
            else:
                from streamlit_gsheets import GSheetsConnection
                conn = st.connection("gsheets", type=GSheetsConnection)
                df_raw = conn.read(spreadsheet=gsheet_url, usecols=[0, 1, 2, 3])
                load_status = "gsheet_private_success"
        except Exception as e:
            st.sidebar.error("❌ Kết nối Google Sheets thất bại.")
            st.sidebar.info("💡 Hệ thống tự động chuyển sang đọc file Excel cục bộ làm dự phòng.")
            if os.path.exists(LOCAL_FILE_PATH):
                df_raw = pd.read_excel(LOCAL_FILE_PATH)
                load_status = "fallback_success"
            else:
                st.sidebar.error("Không tìm thấy cả file Excel dự phòng.")

st.sidebar.subheader("📋 Bộ Quy Tắc Chấm Điểm AI")
st.sidebar.info("Ứng dụng tự động chấm điểm khách hàng dựa trên khung tiêu chuẩn Bất Động Sản Quốc Tế.")

st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">🏢 BẢNG ĐIỀU KHIỂN CHẤM ĐIỂM KHÁCH HÀNG AI</h1>
        <p class="header-subtitle">Hệ thống phân luồng khách hàng tự động thông minh, thiết kế tối ưu với giao diện quét nhanh và bộ lọc đa chiều.</p>
    </div>
""", unsafe_allow_html=True)

if load_status == "local_success":
    st.success("✅ Đã nạp thành công dữ liệu từ file Excel cục bộ `leads_for_gsheet.xlsx`.")
elif load_status == "gsheet_public_success":
    st.success("✅ Đã kết nối thành công và nạp dữ liệu từ Google Sheet công khai.")
elif load_status == "gsheet_private_success":
    st.success("🔒 Đã xác thực bảo mật và nạp dữ liệu từ Google Sheet nội bộ.")
elif load_status == "fallback_success":
    st.warning("⚠️ Không thể kết nối Google Sheets. Đã kích hoạt cơ chế dự phòng: Nạp dữ liệu Excel cục bộ.")

if df_raw.empty:
    st.info("Vui lòng cấu hình nguồn dữ liệu ở thanh bên trái để bắt đầu phân tích.")
else:
    if "scored_df" not in st.session_state or st.sidebar.button("🔄 Chạy lại hệ thống chấm điểm (Làm mới)"):
        with st.spinner("🤖 Trợ lý AI đang quét và phân loại khách hàng..."):
            st.session_state.scored_df = process_leads_dataframe(df_raw.copy())
            st.toast("AI đã chấm điểm xong 500 khách hàng!", icon="🤖")

    df_scored = st.session_state.scored_df

    st.subheader("📊 1. Thống Kê Tổng Quan Khách Hàng")
    
    total_leads = len(df_scored)
    vip_leads = len(df_scored[df_scored["Phân loại"] == "Nóng"])
    warm_leads = len(df_scored[df_scored["Phân loại"] == "Ấm"])
    junk_leads = len(df_scored[df_scored["Phân loại"] == "Rác"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Tổng Khách Hàng Đầu Vào", value=f"{total_leads}", help="Tổng số khách hàng ghi nhận")
    col2.metric(label="Khách VIP (Nóng)", value=f"{vip_leads}", delta="Ưu tiên gọi chốt ngay", delta_color="normal")
    col3.metric(label="Khách Tiềm Năng (Ấm)", value=f"{warm_leads}", delta="Đưa vào chuỗi chăm sóc", delta_color="off")
    col4.metric(label="Khách Không Tốt (Rác)", value=f"{junk_leads}", delta="Nên loại bỏ", delta_color="inverse")
    
    st.divider()

    st.subheader("📝 2. Bảng Kiểm Duyệt (Dành cho Kế Toán / Sales)")
    st.markdown("""
        *Hệ thống đã tự động gán **Từ khóa (Tags)** và **Gợi ý hành động**. Bạn có thể dùng bộ lọc dưới đây để tìm và phê duyệt khách hàng nhanh chóng.*
    """)
    
    st.markdown("##### 🔎 Bộ Lọc Dữ Liệu Thông Minh")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_cat = st.multiselect("Lọc theo Phân loại AI:", options=["Nóng", "Ấm", "Rác"], default=["Nóng", "Ấm", "Rác"])
    with filter_col2:
        filter_status = st.multiselect("Lọc theo Trạng thái duyệt:", options=["Chờ duyệt", "Đã duyệt", "Loại bỏ"], default=["Chờ duyệt", "Đã duyệt", "Loại bỏ"])
        
    filtered_df = df_scored[
        (df_scored["Phân loại"].isin(filter_cat)) & 
        (df_scored["Trạng thái duyệt"].isin(filter_status))
    ]
    
    st.markdown("---")
    
    # Thiết kế cột mới rộng hơn (chỉ 2 cột) để các nút dài không bị xuống dòng
    st.markdown("##### ⚡ Hành Động Nhanh")
    col_quick1, col_quick2 = st.columns(2)
    with col_quick1:
        if st.button("✅ Phê duyệt toàn bộ khách Nóng & Ấm"):
            st.session_state.scored_df.loc[st.session_state.scored_df["Phân loại"].isin(["Nóng", "Ấm"]), "Trạng thái duyệt"] = "Đã duyệt"
            st.toast("Đã duyệt toàn bộ khách hàng Nóng & Ấm!", icon="✅")
            st.rerun()
    with col_quick2:
        if st.button("🗑️ Loại bỏ toàn bộ khách Rác"):
            st.session_state.scored_df.loc[st.session_state.scored_df["Phân loại"] == "Rác", "Trạng thái duyệt"] = "Loại bỏ"
            st.toast("Đã loại bỏ toàn bộ khách Rác!", icon="🗑️")
            st.rerun()
            
    disabled_cols = [col for col in filtered_df.columns if col != "Trạng thái duyệt"]
    
    edited_filtered_df = st.data_editor(
        filtered_df,
        column_config={
            "id": st.column_config.NumberColumn("Mã KH", disabled=True, width="small"),
            "ten_khach": st.column_config.TextColumn("Tên Khách Hàng", disabled=True, width="medium"),
            "sdt": st.column_config.TextColumn("Số Điện Thoại", disabled=True, width="medium"),
            "nhu_cau_mo_ta": st.column_config.TextColumn("Ghi chú Nhu cầu", disabled=True, width="large"),
            "Điểm_AI": st.column_config.NumberColumn("Điểm AI", disabled=True, width="small", format="%d"),
            "Phân loại": st.column_config.TextColumn("Phân loại", disabled=True, width="small"),
            "Từ khóa": st.column_config.TextColumn("Từ khóa (Tags)", disabled=True, width="medium"),
            "Gợi ý hành động": st.column_config.TextColumn("Gợi ý Hành Động", disabled=True, width="medium"),
            "Trạng thái duyệt": st.column_config.SelectboxColumn(
                "Trạng thái duyệt",
                help="Phê duyệt hoặc Loại bỏ",
                width="medium",
                options=["Chờ duyệt", "Đã duyệt", "Loại bỏ"],
                required=True,
            )
        },
        disabled=disabled_cols,
        use_container_width=True,
        hide_index=True
    )
    
    # Đồng bộ trạng thái chỉnh sửa
    st.session_state.scored_df.update(edited_filtered_df)
    
    st.divider()

    st.subheader("📥 3. Trích Xuất & Bàn Giao Dữ Liệu Sạch")
    
    approved_count = len(st.session_state.scored_df[st.session_state.scored_df["Trạng thái duyệt"] == "Đã duyệt"])
    rejected_count = len(st.session_state.scored_df[st.session_state.scored_df["Trạng thái duyệt"] == "Loại bỏ"])
    pending_count = len(st.session_state.scored_df[st.session_state.scored_df["Trạng thái duyệt"] == "Chờ duyệt"])
    
    c1, c2, c3 = st.columns(3)
    c1.info(f"⏳ Số khách đang Chờ duyệt: **{pending_count}**")
    c2.success(f"✅ Số khách Đã duyệt (Sẵn sàng tải): **{approved_count}**")
    c3.error(f"❌ Số khách bị Loại bỏ: **{rejected_count}**")
    
    df_clean = st.session_state.scored_df[st.session_state.scored_df["Trạng thái duyệt"] == "Đã duyệt"]
    
    if approved_count > 0:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_clean.to_excel(writer, index=False, sheet_name='Du_Lieu_Khach_Hang_Sach')
            
            workbook  = writer.book
            worksheet = writer.sheets['Du_Lieu_Khach_Hang_Sach']
            
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#1e293b',
                'font_color': '#ffffff',
                'border': 1
            })
            for col_num, value in enumerate(df_clean.columns.values):
                worksheet.write(0, col_num, value, header_format)
                
            for i, col in enumerate(df_clean.columns):
                max_len = max(df_clean[col].astype(str).map(len).max(), len(col)) + 3
                worksheet.set_column(i, i, min(max_len, 50))
                
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Tải file Excel danh sách khách hàng Đã duyệt",
            data=excel_data,
            file_name="danh_sach_khach_hang_sach.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Chưa có khách hàng nào được 'Đã duyệt'. Hãy phê duyệt ở Bảng Kiểm Duyệt bên trên để có thể tải file.")
