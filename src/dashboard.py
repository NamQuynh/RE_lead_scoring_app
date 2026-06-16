import streamlit as st
import pandas as pd

def apply_custom_css():
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
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    st.sidebar.markdown("""
        <div style='text-align: center; padding: 20px 0;'>
            <h2 style='margin: 0; color: #1e293b; font-family: Outfit; font-weight: 800;'>🏡 Trợ Lý AI BĐS</h2>
            <p style='color: #64748b; font-size: 0.85rem; margin-top: 5px;'>Hệ Thống Phân Bổ Khách Hàng</p>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

def render_header():
    apply_custom_css()
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">🏢 BẢNG ĐIỀU KHIỂN CHẤM ĐIỂM KHÁCH HÀNG AI</h1>
            <p class="header-subtitle">Hệ thống phân luồng khách hàng tự động thông minh, kết nối bảo mật với Google Sheets.</p>
        </div>
    """, unsafe_allow_html=True)

def render_kpis(df):
    st.subheader("📊 1. Thống Kê Tổng Quan Khách Hàng")
    total_leads = len(df)
    vip_leads = len(df[df["Phân loại"] == "HOT"])
    warm_leads = len(df[df["Phân loại"] == "WARM"])
    junk_leads = len(df[df["Phân loại"] == "JUNK"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Tổng Khách Hàng Đầu Vào", value=f"{total_leads}", help="Tổng số khách hàng ghi nhận")
    col2.metric(label="Khách VIP (HOT)", value=f"{vip_leads}", delta="Ưu tiên gọi chốt ngay", delta_color="normal")
    col3.metric(label="Khách Tiềm Năng (WARM)", value=f"{warm_leads}", delta="Đưa vào chuỗi chăm sóc", delta_color="off")
    col4.metric(label="Khách Không Tốt (JUNK)", value=f"{junk_leads}", delta="Nên loại bỏ", delta_color="inverse")
    st.divider()

def render_data_table(df_scored):
    st.subheader("📝 2. Bảng Kiểm Duyệt Khách Hàng (Checkpoint Gate)")
    st.markdown("""
        *Hệ thống đã tự động gán **Tags** và **Next Best Action**. Bạn có thể dùng bộ lọc dưới đây để tìm và phê duyệt khách hàng nhanh chóng.*
    """)
    
    left_col, right_col = st.columns([1, 3])
    
    with left_col:
        st.markdown("##### 🔎 Bộ Lọc Dữ Liệu")
        filter_cat = st.multiselect("Lọc theo Phân loại:", options=["HOT", "WARM", "JUNK"], default=["HOT", "WARM", "JUNK"])
        filter_status = st.multiselect("Lọc theo Trạng thái:", options=["Chờ duyệt", "Đã duyệt", "Loại bỏ"], default=["Chờ duyệt", "Đã duyệt", "Loại bỏ"])
        
        st.markdown("---")
        st.markdown("##### ⚡ Thao tác nhanh")
        if st.button("Duyệt nhanh HOT & WARM", use_container_width=True):
            st.session_state.scored_df.loc[st.session_state.scored_df["Phân loại"].isin(["HOT", "WARM"]), "Trạng thái duyệt"] = "Đã duyệt"
            st.toast("Đã duyệt toàn bộ khách hàng HOT & WARM!", icon="✅")
            st.rerun()
            
        if st.button("🗑️ Loại bỏ toàn bộ JUNK", use_container_width=True):
            st.session_state.scored_df.loc[st.session_state.scored_df["Phân loại"] == "JUNK", "Trạng thái duyệt"] = "Loại bỏ"
            st.toast("Đã loại bỏ toàn bộ khách JUNK!", icon="🗑️")
            st.rerun()
            
        st.markdown("---")
        mask_pii = st.toggle("🔒 Ẩn thông tin cá nhân (PII)", value=True)

    with right_col:
        filtered_df = df_scored[
            (df_scored["Phân loại"].isin(filter_cat)) & 
            (df_scored["Trạng thái duyệt"].isin(filter_status))
        ]
        
        # Xử lý masking PII
        display_df = filtered_df.copy()
        if mask_pii:
            if "sdt" in display_df.columns:
                display_df["sdt"] = display_df["sdt"].astype(str).apply(lambda x: x[:-3] + "***" if len(x) > 3 else x)
            if "email" in display_df.columns:
                display_df["email"] = display_df["email"].astype(str).apply(lambda x: x.split("@")[0][:3] + "***@" + x.split("@")[-1] if "@" in x else x)

        disabled_cols = [col for col in display_df.columns if col != "Trạng thái duyệt"]
        
        edited_filtered_df = st.data_editor(
            display_df,
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
        
        # Chỉ đồng bộ trạng thái duyệt, không đồng bộ lại PII đã masked
        filtered_df["Trạng thái duyệt"] = edited_filtered_df["Trạng thái duyệt"]
        st.session_state.scored_df.update(filtered_df)
        
    st.divider()
