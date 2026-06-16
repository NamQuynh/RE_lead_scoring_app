import pandas as pd
import io
import streamlit as st

def render_export_section(df_scored):
    st.subheader("📥 3. Trích Xuất & Bàn Giao Dữ Liệu Sạch")
    
    approved_count = len(df_scored[df_scored["Trạng thái duyệt"] == "Đã duyệt"])
    rejected_count = len(df_scored[df_scored["Trạng thái duyệt"] == "Loại bỏ"])
    pending_count = len(df_scored[df_scored["Trạng thái duyệt"] == "Chờ duyệt"])
    
    c1, c2, c3 = st.columns(3)
    c1.info(f"⏳ Số khách đang Chờ duyệt: **{pending_count}**")
    c2.success(f"✅ Số khách Đã duyệt (Sẵn sàng tải): **{approved_count}**")
    c3.error(f"❌ Số khách bị Loại bỏ: **{rejected_count}**")
    
    # Kiểm tra điều kiện xuất file: phải không còn Pending, hoặc user chấp nhận bỏ qua
    if pending_count > 0:
        st.warning("⚠️ Hệ thống phát hiện còn Khách hàng ở trạng thái 'Chờ duyệt'. Lời khuyên: Hãy duyệt hết trước khi bàn giao cho Sales.")
        
    if approved_count > 0:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # 1. Sales Handoff
            df_sales = df_scored[df_scored["Trạng thái duyệt"] == "Đã duyệt"].copy()
            sales_columns = [col for col in df_sales.columns if col not in ["Điểm_AI", "Trạng thái duyệt"]]
            df_sales[sales_columns].to_excel(writer, index=False, sheet_name='Sales_Handoff')
            
            # 2. Review Log
            df_review = df_scored.copy()
            review_columns = ["id", "ten_khach", "Điểm_AI", "Phân loại", "Trạng thái duyệt"]
            # Chỉ xuất các cột tồn tại trong data
            review_columns = [c for c in review_columns if c in df_review.columns]
            df_review[review_columns].to_excel(writer, index=False, sheet_name='Review_Log')
            
            # 3. Summary
            summary_data = {
                "Chỉ số": ["Tổng khách hàng bàn giao", "Khách VIP (HOT)", "Khách Rác (Loại bỏ)", "Khách chưa duyệt"],
                "Số lượng": [approved_count, len(df_scored[df_scored["Phân loại"] == "HOT"]), rejected_count, pending_count]
            }
            pd.DataFrame(summary_data).to_excel(writer, index=False, sheet_name='Summary')
            
            # Format headers
            workbook = writer.book
            header_format = workbook.add_format({
                'bold': True, 'text_wrap': True, 'valign': 'top',
                'fg_color': '#1e293b', 'font_color': '#ffffff', 'border': 1
            })
            
            for col_num, value in enumerate(df_sales.columns.values):
                writer.sheets['Sales_Handoff'].write(0, col_num, value, header_format)
                writer.sheets['Sales_Handoff'].set_column(col_num, col_num, 15)
                
            for col_num, value in enumerate(review_columns):
                writer.sheets['Review_Log'].write(0, col_num, value, header_format)
                writer.sheets['Review_Log'].set_column(col_num, col_num, 15)
                
            summary_df = pd.DataFrame(summary_data)
            for col_num, value in enumerate(summary_df.columns.values):
                writer.sheets['Summary'].write(0, col_num, value, header_format)
                writer.sheets['Summary'].set_column(col_num, col_num, 20)
        excel_data = output.getvalue()
        
        st.download_button(
            label="📥 Tải file Excel Bàn Giao (3 Sheets)",
            data=excel_data,
            file_name="danh_sach_ban_giao_sales.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("💡 Vui lòng phê duyệt (chọn 'Đã duyệt') ít nhất 1 khách hàng ở bảng trên để mở khóa tính năng tải báo cáo Excel.")
