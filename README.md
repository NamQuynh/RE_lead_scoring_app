# 🏢 AI Lead Scoring & Automation Dashboard (Buổi 7)

Ứng dụng Streamlit Web App phân loại và chấm điểm khách hàng tiềm năng bất động sản (Real Estate) dựa trên khung tiêu chuẩn **BANT** và cơ chế duyệt dữ liệu **Human-in-the-loop**.

## 🚀 Hướng dẫn Triển khai Streamlit Community Cloud (Product Ready)

Để xuất bản ứng dụng lên **Streamlit Community Cloud** trực tiếp từ GitHub:

### Bước 1: Chuẩn bị Repository trên GitHub
1. Đẩy toàn bộ các tệp tin trong thư mục `buoi_07` này lên một repository mới trên GitHub.
2. Đảm bảo tệp `.gitignore` đã chặn không cho tệp `.streamlit/secrets.toml` bị đẩy lên công khai.

### Bước 2: Triển khai trên Streamlit Cloud
1. Truy cập [share.streamlit.io](https://share.streamlit.io/) và đăng nhập bằng tài khoản GitHub.
2. Bấm nút **New app**, chọn Repository, Branch và trỏ file chính là `app_lead_scoring.py`.
3. Bấm **Deploy!**

### Bước 3: Cấu hình Khóa Bảo Mật (Secrets) trên Đám Mây
Để ứng dụng kết nối được với Google Sheet riêng tư (Private Sheet) của bạn:
1. Trên giao diện quản lý App của Streamlit Cloud, vào phần **Settings** -> **Secrets**.
2. Copy toàn bộ nội dung cấu hình trong tệp `.streamlit/secrets.toml` của bạn và dán vào ô nhập Secrets trên Cloud.
3. Bấm **Save**. Ứng dụng sẽ tự động tải lại và kết nối an toàn.

---

## 💻 Hướng dẫn Chạy Cục Bộ (Local Development)

### 1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy ứng dụng:
```bash
streamlit run app_lead_scoring.py
```

---

## 📋 Cấu trúc Dự án
* `app_lead_scoring.py`: Giao diện chính và luồng xử lý dữ liệu.
* `ai_scoring_engine.py`: Lõi xử lý chấm điểm và logic phân loại dựa trên regex.
* `leads_for_gsheet.xlsx`: File Excel dữ liệu mẫu (Database cục bộ dự phòng).
* `requirements.txt`: Danh sách thư viện phụ thuộc.
* `.streamlit/config.toml`: Cấu hình giao diện (theme màu sắc, font chữ).
* `.streamlit/secrets.toml`: Cấu hình mẫu kết nối Google Sheets bảo mật.
