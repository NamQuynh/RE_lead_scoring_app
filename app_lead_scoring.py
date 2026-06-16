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
    # Nếu chạy từ thư mục khác
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.join(workspace_root, "03_cong_cu"))
    from ai_scoring_engine import process_leads_dataframe

# Cấu hình đường dẫn file Excel cục bộ dự phòng (Nằm cùng thư mục cho bản Self-contained)
LOCAL_FILE_PATH = os.path.join(current_dir, "leads_for_gsheet.xlsx")

# Fallback nếu không có file ở thư mục hiện hành (tìm ở workspace cũ)
if not os.path.exists(LOCAL_FILE_PATH):
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    LOCAL_FILE_PATH = os.path.join(workspace_root, "01_dau_vao", "buoi_07", "leads_for_gsheet.xlsx")

# Cấu hình Page Streamlit
st.set_page_config(
    page_title="AI Lead Scoring Dashboard | Real Estate",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Rich Aesthetics, Glassmorphism, HSL Palette)
st.markdown("""
    <style>
    /* Global Styles */
    .main {
        background-color: #f8fafc;
    }
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
    }
    div, p, span {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
        border-left: 6px solid #3b82f6;
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 10px 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin: 0;
        font-weight: 400;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(226, 232, 240, 0.8);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #3b82f6;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -1px;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
    }
    
    /* Custom Sidebar Card */
    .sidebar-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Streamlit overrides for custom buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 12px 28px !important;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.3) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.4) !important;
    }
    .stButton>button:active {
        transform: translateY(0px) !important;
    }
    
    /* Warning, Info blocks */
    .stAlert {
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 1. SIDEBAR CONFIGURATION (Nhận diện thương hiệu & Kết nối bảo mật)
st.sidebar.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h2 style='margin: 0; color: #1e293b; font-family: Outfit; font-weight: 800;'>🏡 AI Lead Scoring</h2>
        <p style='color: #64748b; font-size: 0.85rem; margin-top: 5px;'>Hệ Thống Phân Phối Dữ Liệu BĐS</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.divider()

st.sidebar.subheader("🔌 Cấu hình Nguồn Dữ Liệu")
data_source = st.sidebar.radio(
    "Chọn phương thức nạp dữ liệu:",
    ("📁 Dùng file Excel cục bộ", "🌐 Kết nối Google Sheets")
)

st.sidebar.divider()

# Nạp dữ liệu chính
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
    # Kết nối Google Sheets (Security Upgrade)
    st.sidebar.markdown("**Mẫu link Google Sheet:**")
    st.sidebar.code("https://docs.google.com/spreadsheets/d/your-id/edit")
    gsheet_url = st.sidebar.text_input("Dán link Google Sheet:", key="gsheet_url_input")
    
    sheet_type = st.sidebar.selectbox("Chế độ truy cập:", ("Trang tính Công khai (Public)", "Trang tính Riêng tư (Private)"))
    
    if gsheet_url:
        try:
            if sheet_type == "Trang tính Công khai (Public)":
                # Convert URL to direct XLSX download link
                if "/edit" in gsheet_url:
                    export_url = gsheet_url.split("/edit")[0] + "/export?format=xlsx"
                else:
                    export_url = gsheet_url
                df_raw = pd.read_excel(export_url)
                load_status = "gsheet_public_success"
            else:
                # Private Sheet - Dùng GSheetsConnection qua secrets
                from streamlit_gsheets import GSheetsConnection
                conn = st.connection("gsheets", type=GSheetsConnection)
                df_raw = conn.read(spreadsheet=gsheet_url, usecols=[0, 1, 2, 3])
                load_status = "gsheet_private_success"
        except Exception as e:
            st.sidebar.error("❌ Kết nối Google Sheets thất bại.")
            st.sidebar.info("💡 Hệ thống tự động chuyển sang đọc file Excel cục bộ làm dự phòng (Fallback).")
            # Fallback
            if os.path.exists(LOCAL_FILE_PATH):
                df_raw = pd.read_excel(LOCAL_FILE_PATH)
                load_status = "fallback_success"
            else:
                st.sidebar.error("Không tìm thấy cả file Excel dự phòng.")

st.sidebar.subheader("📋 Tri thức Chấm điểm (BANT)")
st.sidebar.info("Ứng dụng tự động chấm điểm dựa trên khung tiêu chuẩn CRM Bất Động Sản Quốc tế.")

# 2. MAIN PAGE BANNER
st.markdown("""
    <div class="header-banner">
        <h1 class="header-title">🏢 AI LEAD SCORING & CHECKPOINT SYSTEM</h1>
        <p class="header-subtitle">Hệ thống phân luồng khách hàng tự động với "Glanceable UX" và bộ lọc đa chiều (Advanced Filters)</p>
    </div>
""", unsafe_allow_html=True)

# Hiển thị thông báo trạng thái tải dữ liệu
if load_status == "local_success":
    st.success("✅ Đã nạp thành công dữ liệu từ file Excel cục bộ `leads_for_gsheet.xlsx`.")
elif load_status == "gsheet_public_success":
    st.success("✅ Đã kết nối thành công và nạp dữ liệu từ Google Sheet công khai (Public).")
elif load_status == "gsheet_private_success":
    st.success("🔒 Đã xác thực bảo mật và nạp dữ liệu từ Google Sheet riêng tư (Private).")
elif load_status == "fallback_success":
    st.warning("⚠️ Không thể kết nối Google Sheets. Đã kích hoạt cơ chế dự phòng: Nạp dữ liệu Excel cục bộ.")

# Kiểm tra dữ liệu
if df_raw.empty:
    st.info("Vui lòng cấu hình nguồn dữ liệu ở thanh Sidebar để bắt đầu phân tích.")
else:
    # Tự động chấm điểm (Chỉ chấm điểm 1 lần và lưu vào session_state để tránh mất trạng thái sửa của user)
    if "scored_df" not in st.session_state or st.sidebar.button("🔄 Chạy lại bộ chấm điểm AI (Reset)"):
        with st.spinner("🤖 Trợ lý AI đang quét dữ liệu BANT và phân loại Leads..."):
            st.session_state.scored_df = process_leads_dataframe(df_raw.copy())
            st.toast("AI đã chấm điểm xong 500 khách hàng!", icon="🤖")

    df_scored = st.session_state.scored_df

    # 3. DASHBOARD METRICS (Thống kê Tổng quan)
    st.subheader("📊 1. Chỉ Số Phân Bổ Chất Lượng Khách Hàng")
    
    total_leads = len(df_scored)
    vip_leads = len(df_scored[df_scored["Category"] == "HOT"])
    warm_leads = len(df_scored[df_scored["Category"] == "WARM"])
    junk_leads = len(df_scored[df_scored["Category"] == "JUNK"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Tổng số Lead đầu vào", value=f"{total_leads} khách", help="Tổng số khách hàng ghi nhận từ Sheets")
    col2.metric(label="Khách VIP (HOT +50đ)", value=f"{vip_leads} khách", delta="Ưu tiên Sales gọi ngay", delta_color="normal")
    col3.metric(label="Khách Tiềm năng (WARM)", value=f"{warm_leads} khách", delta="Nuôi dưỡng thêm", delta_color="off")
    col4.metric(label="Khách rác (JUNK -50đ)", value=f"{junk_leads} khách", delta="Nên loại bỏ", delta_color="inverse")
    
    st.divider()

    # 4. HUMAN-IN-THE-LOOP CHECKPOINT (Bảng kiểm duyệt)
    st.subheader("📝 2. Bảng Kiểm Duyệt Khách Hàng (Checkpoint Gate)")
    st.markdown("""
        *Hệ thống đã tự động gán **Tags** và **Next Best Action** (Gợi ý hành động tiếp theo). Kế toán/Sales có thể dùng bộ lọc (Filters) dưới đây để duyệt nhanh theo nhóm khách hàng.*
    """)
    
    # --- BỘ LỌC ĐA CHIỀU (ADVANCED FILTERS) ---
    st.markdown("##### 🔎 Bộ Lọc Dữ Liệu (Progressive Disclosure)")
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        filter_cat = st.multiselect("Lọc theo Phân loại (Category):", options=["HOT", "WARM", "JUNK"], default=["HOT", "WARM", "JUNK"])
    with filter_col2:
        filter_status = st.multiselect("Lọc theo Trạng thái duyệt:", options=["Chờ duyệt", "Đã duyệt", "Loại bỏ"], default=["Chờ duyệt", "Đã duyệt", "Loại bỏ"])
        
    # Áp dụng bộ lọc lên dataframe
    filtered_df = df_scored[
        (df_scored["Category"].isin(filter_cat)) & 
        (df_scored["Status"].isin(filter_status))
    ]
    
    st.markdown("---")
    
    # --- TÍNH NĂNG DUYỆT NHANH (QUICK ACTIONS) ---
    col_quick1, col_quick2, col_quick3 = st.columns([1, 1, 2])
    with col_quick1:
        if st.button("⚡ Duyệt nhanh toàn bộ HOT & WARM"):
            st.session_state.scored_df.loc[st.session_state.scored_df["Category"].isin(["HOT", "WARM"]), "Status"] = "Đã duyệt"
            st.toast("Đã chuyển trạng thái toàn bộ khách hàng HOT & WARM sang 'Đã duyệt'!", icon="⚡")
            st.rerun()
    with col_quick2:
        if st.button("🗑️ Loại bỏ toàn bộ JUNK"):
            st.session_state.scored_df.loc[st.session_state.scored_df["Category"] == "JUNK", "Status"] = "Loại bỏ"
            st.toast("Đã loại bỏ toàn bộ khách hàng JUNK!", icon="🗑️")
            st.rerun()
            
    # Cấu hình danh sách cột khóa
    disabled_cols = [col for col in filtered_df.columns if col != "Status"]
    
    # Bảng chỉnh sửa tương tác
    edited_filtered_df = st.data_editor(
        filtered_df,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True, width="small"),
            "ten_khach": st.column_config.TextColumn("Tên Khách Hàng", disabled=True, width="medium"),
            "sdt": st.column_config.TextColumn("Số Điện Thoại", disabled=True, width="medium"),
            "nhu_cau_mo_ta": st.column_config.TextColumn("Mô tả nhu cầu (Gốc)", disabled=True, width="large"),
            "AI_Score": st.column_config.NumberColumn("Điểm", disabled=True, width="small", format="%d"),
            "Category": st.column_config.TextColumn("Xếp hạng", disabled=True, width="small"),
            "Tags": st.column_config.TextColumn("Từ khóa (Tags)", disabled=True, width="medium"),
            "Next_Action": st.column_config.TextColumn("Gợi ý Hành động", disabled=True, width="medium"),
            "Status": st.column_config.SelectboxColumn(
                "Trạng thái duyệt",
                help="Phê duyệt hoặc Loại bỏ khách hàng",
                width="medium",
                options=["Chờ duyệt", "Đã duyệt", "Loại bỏ"],
                required=True,
            )
        },
        disabled=disabled_cols,
        use_container_width=True,
        hide_index=True
    )
    
    # Đồng bộ trạng thái chỉnh sửa thủ công từ bảng lọc về session_state gốc
    st.session_state.scored_df.update(edited_filtered_df)
    
    st.divider()

    # 5. DATA HANDOFF & EXPORT (Bàn giao dữ liệu sạch)
    st.subheader("📥 3. Xuất Bản & Bàn Giao Dữ Liệu Sạch (System Handoff)")
    
    # Thống kê trạng thái duyệt của user
    approved_count = len(st.session_state.scored_df[st.session_state.scored_df["Status"] == "Đã duyệt"])
    rejected_count = len(st.session_state.scored_df[st.session_state.scored_df["Status"] == "Loại bỏ"])
    pending_count = len(st.session_state.scored_df[st.session_state.scored_df["Status"] == "Chờ duyệt"])
    
    c1, c2, c3 = st.columns(3)
    c1.info(f"⏳ Số khách đang Chờ duyệt: **{pending_count}**")
    c2.success(f"✅ Số khách Đã duyệt (Sẽ xuất file): **{approved_count}**")
    c3.error(f"❌ Số khách bị Loại bỏ: **{rejected_count}**")
    
    # Lọc ra tập dữ liệu sạch để xuất
    df_clean = st.session_state.scored_df[st.session_state.scored_df["Status"] == "Đã duyệt"]
    
    if approved_count > 0:
        # Xuất dữ liệu sang file Excel Excel Sạch bằng openpyxl / xlsxwriter
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_clean.to_excel(writer, index=False, sheet_name='Clean_Leads_Handoff')
            
            # Format sheet Excel cho chuyên nghiệp
            workbook  = writer.book
            worksheet = writer.sheets['Clean_Leads_Handoff']
            
            # Style header chưng diện
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
                
            # Tự động co giãn cột vừa khít nội dung
            for i, col in enumerate(df_clean.columns):
                max_len = max(df_clean[col].astype(str).map(len).max(), len(col)) + 3
                worksheet.set_column(i, i, min(max_len, 50)) # giới hạn cột dài tối đa 50 ký tự
                
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Tải file Excel sạch bàn giao cho bộ phận Sales",
            data=excel_data,
            file_name="clean_leads_handoff.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.warning("⚠️ Hiện tại chưa có khách hàng nào được chuyển trạng thái sang 'Đã duyệt'. Hãy phê duyệt khách hàng ở bảng Kiểm duyệt mục 2 để xuất file.")
