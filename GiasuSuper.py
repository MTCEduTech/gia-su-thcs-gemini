import streamlit as st
import os
import time
from google import genai
from google.genai import types
import streamlit.components.v1 as components # 👈 ĐÃ THÊM: Import component để chèn HTML an toàn

# ==================== 🎨 CSS TÙY CHỈNH ====================
st.markdown("""
<style>

/* ===================== 🌟 BANNER ===================== */
/* ẨN HEADER STREAMLIT (Logo + menu) */
header, [data-testid="stHeader"] {
    display: none !important;
}

.custom-top-banner-wrapper {
    position: relative;
    width: 100vw;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;

    background: #87CEEB;


    /* ⭐ FLEXBOX: căn giữa theo chiều dọc và ngang */
    display: flex;
    flex-direction: column;
    align-items: center;       /* căn giữa ngang */
    justify-content: center;   /* căn giữa dọc */

    height: 130px;             /* CHIỀU CAO CỐ ĐỊNH GIÚP CĂN CHỮ CHUẨN */
    text-align: center;
}

/* Tiêu đề */
.custom-top-banner-title {
    color: blue;
    font-weight: 800;
    font-size: 2.3em;
    margin: 0;                 /* xoá margin tự nhiên */
}

/* Dòng mô tả */
.custom-top-banner-sub {
    color: white;
    font-size: 1.15em;
    font-weight: 500;
    margin-top: 4px;
}

/* ===================== 🎨 NỀN & BỐ CỤC TỔNG THỂ ===================== */
[data-testid="stAppViewContainer"] {
    background-color: #87CEEB;   /* ⭐ Nền xanh nhạt rất dễ nhìn */
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #202020;
}

/* ===================== 🏷 TIÊU ĐỀ SECTION ===================== */
.section-title, h2, h3 {
    font-weight: 700;
    color: #003EA8;
}

/* ===================== 📦 BOX UPLOAD ===================== */
.stFileUploader {
    border: 2px dashed #1E50FF;
    background: #ffffff;
    border-radius: 14px;
    padding: 18px;
}
.stFileUploader:hover {
    background: #f0f5ff;
    border-color: #0048D6;
}

/* ===================== 💬 KHUNG CHAT ===================== */
.stChatMessage {
    border-radius: 14px;
    padding: 14px 20px;
    font-size: 1.05em;
    background: #FFFFFF;
    border: 1px solid #e0e6f5;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
/* User */
.stChatMessage[data-testid="stChatMessageUser"] {
    margin-left: 20%;
    border-left: 4px solid #006AFF;
}
/* Assistant */
.stChatMessage[data-testid="stChatMessageAssistant"] {
    margin-right: 20%;
    background: #87CEEB;
    border-left: 4px solid #003EA8;
}

/* ===================== ✏️ Ô GỬI TIN NHẮN ===================== */
[data-testid="stChatInput"] {
    background-color: white;
    border-radius: 14px;
    padding: 12px;
    border-top: 2px solid #dfe6ff;
    box-shadow: 0 -3px 10px rgba(0,0,0,0.05);
}
[data-testid="stChatInput"] button {
    background: #FFFFFF !important;
    color: blue !important;
    border-radius: 8px;
    font-weight: 600;
}
[data-testid="stChatInput"] button:hover {
    background: #87CEEB !important;
}

/* ===================== 🔵 FOOTER FULL-WIDTH ===================== */
footer {visibility: hidden;}

.custom-footer-container {
    position: fixed;              /* LUÔN CỐ ĐỊNH Ở CHÂN TRANG */
    bottom: 0;
    left: 0;
    width: 100vw;                 /* TRÀN FULL MÀN HÌNH */
    background: #003EA8;
    padding: 12px 0;
    text-align: center;
    color: white;
    font-size: 0.9em;
    box-shadow: 0 -3px 10px rgba(0,0,0,0.18);
    z-index: 999999;              /* ƯU TIÊN HIỂN THỊ */
}

/* 🧱 TẠO KHOẢNG TRỐNG ĐỂ NỘI DUNG KHÔNG CHE FOOTER */
html, body, [data-testid="stAppViewContainer"] {
    padding-bottom: 90px !important;
}

/* ===================== ICON CHAT ===================== */
.chat-icon {
    font-size: 20px;
    margin-right: 8px;
}


</style>

""", unsafe_allow_html=True)


# ==================== ⚙️ CẤU HÌNH GEMINI CLIENT ====================
@st.cache_resource
def get_gemini_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        return genai.Client(api_key=api_key)
    except (AttributeError, KeyError):
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            return genai.Client(api_key=api_key)
        except Exception:
            st.error("❌ Không tìm thấy Gemini API Key. Hãy đặt trong Streamlit Secrets hoặc biến môi trường.")
            st.stop()

client = get_gemini_client()

# ==================== 💬 KHỞI TẠO PHIÊN CHAT ====================
if "chat_session" not in st.session_state:
    config = types.GenerateContentConfig(
        # Đã sửa: Thêm hướng dẫn để AI luôn xưng là 'Thầy'
        system_instruction="Bạn là Thầy Chánh - Gia Sư AI THCS thân thiện, giúp học sinh lớp 6–9 học tất cả các môn. Bạn phải luôn xưng là 'Thầy' hoặc 'Thầy Chánh' khi giao tiếp. Giải thích dễ hiểu, có ví dụ cụ thể.",
        temperature=1
    )
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=config
    )

# ==================== 🧠 GIAO DIỆN NGƯỜI DÙNG ====================
st.markdown("""
<div class="custom-top-banner-wrapper">
    <div class="custom-top-banner-title">🎓 GIA SƯ AI 24/7 – HỖ TRỢ HỌC TẬP</div>
    <div class="custom-top-banner-sub">Trợ lý học tập thông minh do Thầy Mai Thiện Chánh phát triển</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("📚 **Nhập câu hỏi hoặc tải ảnh bài tập để được hướng dẫn chi tiết:**")

uploaded_file = st.file_uploader("📸 Tải ảnh bài tập", type=["png", "jpg", "jpeg"])
image_part, image_bytes = None, None
if uploaded_file:
    image_bytes = uploaded_file.read()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_file.type)
    st.sidebar.image(image_bytes, caption='Ảnh bài tập đã tải', width=250)
    st.success("✅ Ảnh đã tải thành công!")

st.markdown("---") # Giữ nguyên đường ngăn cách
# ==================== 🕐 HIỂN THỊ LỊCH SỬ CHAT ====================
for msg in st.session_state.chat_session.get_history():
    role = "Thầy Chánh" if msg.role == "model" else "Học sinh"
    icon = "🤖" if role == "Thầy Chánh" else "👩‍🎓"
    with st.chat_message(role):
        st.markdown(f"<span class='chat-icon'>{icon}</span>{msg.parts[0].text}", unsafe_allow_html=True)

# ==================== ✍️ NHẬP CHAT CẬP NHẬT NGÀY THÁNG ====================
from datetime import datetime
from lunardate import LunarDate

# Hàm tính Can Chi năm âm lịch
def can_chi_year(year):
    can_list = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
    chi_list = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]

    can = can_list[(year + 6) % 10]
    chi = chi_list[(year + 8) % 12]
    return f"{can} {chi}"


if prompt := st.chat_input("💬 Gõ câu hỏi của bạn tại đây..."):

    # 🎯 LẤY NGÀY GIỜ THỰC TẾ TỪ HỆ THỐNG
    now = datetime.now()

    # 🎯 Dương lịch
    real_time_dl = (
        f"Hôm nay là ngày {now.day} tháng {now.month} năm {now.year}, "
        f"Thứ {now.strftime('%A')}."
    )

    # 🎯 TÍNH ÂM LỊCH BẰNG lunardate
    lunar = LunarDate.fromSolarDate(now.year, now.month, now.day)
    ngay_am = lunar.day
    thang_am = lunar.month
    nam_am = lunar.year

    # Tính Can Chi năm âm lịch
    ten_nam = can_chi_year(nam_am)

    # 🎯 Chuỗi âm lịch hiển thị
    real_time_am = (
        f"Theo Âm lịch, hôm nay là ngày {ngay_am} tháng {thang_am} năm {ten_nam}."
    )

    # 🎯 CHÈN THÔNG ĐIỆP ÉP BUỘC AI LUÔN DÙNG ĐÚNG NGÀY ÂM + DƯƠNG LỊCH
    system_time_note = (
        "LƯU Ý CHO MÔ HÌNH: Đây là ngày giờ thực tế của hệ thống máy chủ. "
        + real_time_dl + " "
        + real_time_am +
        " Khi học sinh hỏi về ngày tháng, âm lịch, dương lịch, thời gian, "
        "bạn **PHẢI** dùng đúng các thông tin này và **KHÔNG ĐƯỢC** suy đoán, "
        "tự tạo hoặc dùng ngày khác."
    )

    contents = [
        types.Part(text=system_time_note),
        types.Part(text=prompt)  # 📌 Prompt học sinh
    ]

    if image_part:
        contents.insert(0, image_part)
        with st.chat_message("Học sinh"):
            st.markdown(
                f"<span class='chat-icon'>👩‍🎓</span>**Bài tập đính kèm:**",
                unsafe_allow_html=True
            )
            st.image(image_bytes, width=180)
            st.markdown(prompt)
    else:
        with st.chat_message("Học sinh"):
            st.markdown(
                f"<span class='chat-icon'>👩‍🎓</span>{prompt}",
                unsafe_allow_html=True
            )

    with st.spinner("⏳ Thầy Chánh đang suy nghĩ..."):
        response = st.session_state.chat_session.send_message(contents)

    # Hiệu ứng gõ chữ
    with st.chat_message("Thầy Chánh"):
        placeholder = st.empty()
        text_display = ""
        for char in response.text:
            text_display += char
            placeholder.markdown(
                f"<span class='chat-icon'>🤖</span>{text_display}",
                unsafe_allow_html=True
            )
            time.sleep(0.008)

        st.session_state.last_response = response.text


# ==================== 🧾 FOOTER ====================
st.markdown("""
<div class="custom-footer-container">
    © 2025 Gia Sư AI THCS – Phát triển bởi Thầy Chánh |
    Trường THCS Đức Phú, Lâm Đồng |
    <a href="https://dayhoctichcuc.netlify.app/" target="_blank" style="color: white; text-decoration: none;">
        🏠 Về trang chủ BỘ CÔNG CỤ DẠY HỌC TÍCH CỰC
    </a>
</div>
""", unsafe_allow_html=True)














































