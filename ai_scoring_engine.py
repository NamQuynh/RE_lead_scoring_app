import pandas as pd
import re

def score_lead_logic(note):
    """
    Hàm phân loại và chấm điểm khách hàng tiềm năng dựa theo Tiêu chí thực hành Buổi 7.
    - Cộng 50 điểm cho khách hàng VIP / siêu tiềm năng.
    - Trừ 50 điểm cho khách hàng rác / không tiềm năng.
    - Giữ nguyên điểm (0 điểm) hoặc cộng ít (10 điểm) cho các trường hợp khác.
    """
    note_lower = str(note).lower()
    score = 0
    reasons = []
    
    # 1. TIÊU CHÍ CỘNG 50 ĐIỂM (KHÁCH HÀNG VIP / SIÊU TIỀM NĂNG)
    vip_matched = False
    
    # - Ngân sách lớn: Số tiền >= 20 tỷ hoặc các cụm từ chỉ định
    budget_large = False
    if any(kw in note_lower for kw in ["tài chính mạnh", "không thành vấn đề"]):
        budget_large = True
        reasons.append("Ngân sách lớn (Tài chính mạnh)")
    else:
        # Tìm các số đi kèm chữ "tỷ"
        numbers = re.findall(r'(\d+)\s*tỷ', note_lower)
        for num_str in numbers:
            if int(num_str) >= 20:
                budget_large = True
                reasons.append(f"Ngân sách lớn (>= 20 tỷ: {num_str} tỷ)")
                break
                
    # - Loại hình cao cấp
    high_end_type = False
    vip_types = [
        "biệt thự đơn lập", "biệt thự", "penthouse", 
        "shophouse mặt đường lớn", "shophouse", 
        "quỹ đất công nghiệp", "đất công nghiệp",
        "sàn văn phòng diện tích lớn", "văn phòng diện tích lớn"
    ]
    for vt in vip_types:
        if vt in note_lower:
            high_end_type = True
            reasons.append(f"Loại hình cao cấp ({vt})")
            break
            
    # - Vị trí đắc địa
    prime_location = False
    vip_locations = ["quận 1", "ven sông", "vinhomes ocean park", "phú mỹ hưng"]
    for vl in vip_locations:
        if vl in note_lower:
            # Loại trừ trường hợp yêu cầu phi thực tế (ví dụ: nhà Q1 giá 1 tỷ)
            if not ("1 tỷ" in note_lower or "2 tỷ" in note_lower or "vài trăm triệu" in note_lower or "2 triệu" in note_lower):
                prime_location = True
                reasons.append(f"Vị trí đắc địa ({vl})")
                break
            
    # - Đối tượng khách hàng
    vip_persona = False
    vip_personas = ["chủ doanh nghiệp", "nhà đầu tư chuyên nghiệp", "mua sỉ", "mua số lượng lớn"]
    for vp in vip_personas:
        if vp in note_lower:
            vip_persona = True
            reasons.append(f"Đối tượng VIP ({vp})")
            break
            
    # - Tính cấp thiết & Minh bạch
    urgency_transparency = False
    vip_urgencies = ["pháp lý chuẩn 100%", "sổ hồng riêng", "gặp trực tiếp chủ đầu tư để đàm phán", "trực tiếp chủ đầu tư"]
    for vu in vip_urgencies:
        if vu in note_lower:
            # Loại trừ trường hợp đất nền 2-3 tỷ (mục 3 - trường hợp khác)
            if not ("2-3 tỷ" in note_lower or "2 tỷ" in note_lower or "3 tỷ" in note_lower):
                urgency_transparency = True
                reasons.append(f"Cấp thiết & Minh bạch ({vu})")
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
            reasons.append("Yêu cầu phi thực tế (Nhà Q1 giá rẻ)")
    if "trung tâm" in note_lower and any(kw in note_lower for kw in ["vài trăm triệu", "giá 2 triệu", "2 triệu"]):
        unrealistic_request = True
        reasons.append("Yêu cầu phi thực tế (Trung tâm giá rẻ)")
        
    # - Không có nhu cầu
    no_need = False
    if any(kw in note_lower for kw in ["nhầm số", "không có nhu cầu", "dữ liệu cũ", "nhầm ngành", "gọi nhầm"]):
        no_need = True
        reasons.append("Không có nhu cầu thực tế")
        
    # - Khách hàng không thiện chí
    uncooperative = False
    if any(kw in note_lower for kw in ["hỏi giá cho vui", "chưa có ý định mua", "thái độ không hợp tác", "không thiện chí"]):
        uncooperative = True
        reasons.append("Khách hàng không thiện chí")
        
    # - Spam/Quảng cáo
    spam_ad = False
    if any(kw in note_lower for kw in ["bảo hiểm", "vay vốn", "mời chào", "quảng cáo", "spam"]):
        spam_ad = True
        reasons.append("Spam hoặc quảng cáo dịch vụ")
        
    # - Thông tin liên lạc lỗi
    contact_issue = False
    if any(kw in note_lower for kw in ["thuê bao", "không bắt máy", "không phản hồi zalo"]):
        contact_issue = True
        reasons.append("Lỗi thông tin liên lạc")
        
    if unrealistic_request or no_need or uncooperative or spam_ad or contact_issue:
        score -= 50
        junk_matched = True
        
    # 3. CÁC TRƯỜNG HỢP KHÁC (GIỮ NGUYÊN ĐIỂM HOẶC CỘNG ÍT)
    # Nếu không phải VIP và không phải JUNK
    if not vip_matched and not junk_matched:
        # Mặc định cộng 10 điểm cho khách hàng có nhu cầu bình thường/tầm trung
        score += 10
        if any(kw in note_lower for kw in ["chung cư", "căn hộ", "nhà phố", "tầm trung", "3-10 tỷ"]):
            reasons.append("Nhu cầu tầm trung (Chung cư/Nhà phố)")
        elif "vay ngân hàng" in note_lower or "hỗ trợ vay" in note_lower:
            reasons.append("Cần hỗ trợ tài chính / vay ngân hàng")
        elif "đất nền" in note_lower or "sổ hồng riêng" in note_lower:
            reasons.append("Đất nền vùng ven / Nhu cầu thực")
        else:
            reasons.append("Nhu cầu tiềm năng thông thường")
            
    reason_str = " | ".join(reasons) if reasons else "Thông thường"
    
    # Phân loại Category
    if score >= 50:
        category = "HOT"
    elif score <= -50:
        category = "JUNK"
    else:
        category = "WARM"
        
    return score, category, reason_str

def process_leads_dataframe(df):
    """
    Xử lý hàng loạt danh sách lead (Batch Processing) từ file Excel / DataFrame.
    """
    # Tìm cột chứa nội dung nhu cầu / ghi chú
    note_col = None
    possible_cols = ["nhu_cau_mo_ta", "Ghi chú", "nhu_cau", "note", "ghi_chu"]
    for col in possible_cols:
        if col in df.columns:
            note_col = col
            break
            
    if not note_col:
        # Quét cột nào có tên gần giống
        for col in df.columns:
            if "nhu cầu" in col.lower() or "ghi chú" in col.lower() or "note" in col.lower():
                note_col = col
                break
                
    if not note_col:
        raise ValueError("Không tìm thấy cột chứa mô tả nhu cầu khách hàng.")
        
    # Áp dụng logic chấm điểm
    results = df[note_col].apply(score_lead_logic)
    
    df["AI_Score"] = [res[0] for res in results]
    df["Category"] = [res[1] for res in results]
    df["Reasoning"] = [res[2] for res in results]
    
    # Thiết lập trạng thái mặc định cho Human-in-the-loop
    df["Status"] = "Chờ duyệt"
    
    return df
