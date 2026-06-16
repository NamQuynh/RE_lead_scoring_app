import pandas as pd
import re

def score_lead_logic(note):
    """
    Hàm phân loại và chấm điểm khách hàng tiềm năng dựa theo Tiêu chí thực hành Buổi 7.
    Bản nâng cấp (BA Audit): Trả về Từ khóa (Tags) ngắn gọn và Hành động tiếp theo thay vì dòng text dài.
    Thuần Việt 100% cho Non-tech User.
    """
    note_lower = str(note).lower()
    score = 0
    tags = []
    
    # 1. TIÊU CHÍ CỘNG 50 ĐIỂM (KHÁCH HÀNG VIP / SIÊU TIỀM NĂNG)
    vip_matched = False
    
    # - Ngân sách lớn
    budget_large = False
    if any(kw in note_lower for kw in ["tài chính mạnh", "không thành vấn đề"]):
        budget_large = True
        tags.append("💰 Tài chính mạnh")
    else:
        numbers = re.findall(r'(\d+)\s*tỷ', note_lower)
        for num_str in numbers:
            if int(num_str) >= 20:
                budget_large = True
                tags.append(f"💰 Ngân sách >20T")
                break
                
    # - Loại hình cao cấp
    high_end_type = False
    vip_types = {
        "biệt thự đơn lập": "Biệt thự ĐL", "biệt thự": "Biệt thự", "penthouse": "Penthouse", 
        "shophouse mặt đường lớn": "Shophouse Vip", "shophouse": "Shophouse", 
        "quỹ đất công nghiệp": "Đất CN", "đất công nghiệp": "Đất CN",
        "sàn văn phòng diện tích lớn": "VP Lớn", "văn phòng diện tích lớn": "VP Lớn"
    }
    for kw, tag in vip_types.items():
        if kw in note_lower:
            high_end_type = True
            tags.append(f"🏰 {tag}")
            break
            
    # - Vị trí đắc địa
    prime_location = False
    vip_locations = {"quận 1": "Quận 1", "ven sông": "Ven sông", "vinhomes ocean park": "Vinhomes OCP", "phú mỹ hưng": "Phú Mỹ Hưng"}
    for kw, tag in vip_locations.items():
        if kw in note_lower:
            # Loại trừ trường hợp yêu cầu phi thực tế (ví dụ: nhà Q1 giá 1 tỷ)
            if not any(exc in note_lower for exc in ["1 tỷ", "2 tỷ", "vài trăm triệu", "2 triệu"]):
                prime_location = True
                tags.append(f"📍 {tag}")
                break
            
    # - Đối tượng khách hàng
    vip_persona = False
    vip_personas = {"chủ doanh nghiệp": "Chủ DN", "nhà đầu tư chuyên nghiệp": "NĐT VIP", "mua sỉ": "Mua Sỉ", "mua số lượng lớn": "Mua Sỉ"}
    for kw, tag in vip_personas.items():
        if kw in note_lower:
            vip_persona = True
            tags.append(f"👤 {tag}")
            break
            
    # - Tính cấp thiết & Minh bạch
    urgency_transparency = False
    vip_urgencies = {"pháp lý chuẩn 100%": "Pháp lý sạch", "sổ hồng riêng": "Sổ riêng", "gặp trực tiếp chủ đầu tư": "Gặp CĐT", "trực tiếp chủ đầu tư": "Trực tiếp CĐT"}
    for kw, tag in vip_urgencies.items():
        if kw in note_lower:
            if not any(exc in note_lower for exc in ["2-3 tỷ", "2 tỷ", "3 tỷ"]):
                urgency_transparency = True
                tags.append(f"⚖️ {tag}")
                break
            
    if budget_large or high_end_type or prime_location or vip_persona or urgency_transparency:
        score += 50
        vip_matched = True

    # 2. TIÊU CHÍ TRỪ 50 ĐIỂM (KHÁCH HÀNG RÁC / KHÔNG TIỀM NĂNG)
    junk_matched = False
    
    # - Yêu cầu phi thực tế
    unrealistic_request = False
    if "quận 1" in note_lower or "q1" in note_lower:
        if any(kw in note_lower for kw in ["1 tỷ", "1-2 tỷ", "2 tỷ", "vài trăm triệu"]):
            unrealistic_request = True
            tags.append("🤡 Nhu cầu ảo (Q1 rẻ)")
    if "trung tâm" in note_lower and any(kw in note_lower for kw in ["vài trăm triệu", "giá 2 triệu", "2 triệu"]):
        unrealistic_request = True
        tags.append("🤡 Nhu cầu ảo (TT rẻ)")
        
    # - Không có nhu cầu
    no_need = False
    if any(kw in note_lower for kw in ["nhầm số", "không có nhu cầu", "dữ liệu cũ", "nhầm ngành", "gọi nhầm"]):
        no_need = True
        tags.append("📵 Sai số/Không nhu cầu")
        
    # - Khách hàng không thiện chí
    uncooperative = False
    if any(kw in note_lower for kw in ["hỏi giá cho vui", "chưa có ý định mua", "thái độ không hợp tác", "không thiện chí"]):
        uncooperative = True
        tags.append("😒 Không thiện chí")
        
    # - Spam/Quảng cáo
    spam_ad = False
    if any(kw in note_lower for kw in ["bảo hiểm", "vay vốn", "mời chào", "quảng cáo", "spam"]):
        spam_ad = True
        tags.append("🗑️ Spam/Quảng cáo")
        
    # - Thông tin liên lạc lỗi
    contact_issue = False
    if any(kw in note_lower for kw in ["thuê bao", "không bắt máy", "không phản hồi zalo"]):
        contact_issue = True
        tags.append("🔇 Không liên lạc được")
        
    if unrealistic_request or no_need or uncooperative or spam_ad or contact_issue:
        score -= 50
        junk_matched = True
        
    # 3. CÁC TRƯỜNG HỢP KHÁC (GIỮ NGUYÊN ĐIỂM HOẶC CỘNG ÍT)
    if not vip_matched and not junk_matched:
        score += 10
        if any(kw in note_lower for kw in ["chung cư", "căn hộ", "nhà phố", "tầm trung", "3-10 tỷ"]):
            tags.append("🏢 Nhu cầu Phổ thông")
        elif "vay ngân hàng" in note_lower or "hỗ trợ vay" in note_lower:
            tags.append("🏦 Cần vay NH")
        elif "đất nền" in note_lower or "sổ hồng riêng" in note_lower:
            tags.append("🏕️ Đất nền")
        else:
            tags.append("✅ Nhu cầu trung bình")
            
    tags_str = " | ".join(tags) if tags else "✅ Thông thường"
    
    # Phân loại (Category) & Đề xuất hành động
    if score >= 50:
        category = "Nóng"
        next_action = "📞 Gọi chốt deal (trong 5p)"
    elif score <= -50:
        category = "Rác"
        next_action = "🚫 Loại bỏ / Chặn số"
    else:
        category = "Ấm"
        next_action = "📧 Đưa vào chuỗi chăm sóc Zalo"
        
    return score, category, tags_str, next_action

def process_leads_dataframe(df):
    """
    Xử lý hàng loạt danh sách khách hàng từ file Excel / DataFrame.
    """
    # Tìm cột chứa nội dung nhu cầu / ghi chú
    note_col = None
    possible_cols = ["nhu_cau_mo_ta", "Ghi chú", "nhu_cau", "note", "ghi_chu"]
    for col in possible_cols:
        if col in df.columns:
            note_col = col
            break
            
    if not note_col:
        for col in df.columns:
            if "nhu cầu" in col.lower() or "ghi chú" in col.lower() or "note" in col.lower():
                note_col = col
                break
                
    if not note_col:
        raise ValueError("Không tìm thấy cột chứa mô tả nhu cầu khách hàng.")
        
    # Áp dụng logic chấm điểm
    results = df[note_col].apply(score_lead_logic)
    
    df["Điểm_AI"] = [res[0] for res in results]
    df["Phân loại"] = [res[1] for res in results]
    df["Từ khóa"] = [res[2] for res in results]
    df["Gợi ý hành động"] = [res[3] for res in results]
    
    # Xóa các cột cũ tiếng Anh nếu có
    for old_col in ["AI_Score", "Category", "Tags", "Next_Action", "Reasoning", "Status"]:
        if old_col in df.columns:
            df.drop(columns=[old_col], inplace=True)
    
    # Thiết lập trạng thái mặc định cho khâu kiểm duyệt
    df["Trạng thái duyệt"] = "Chờ duyệt"
    
    return df
