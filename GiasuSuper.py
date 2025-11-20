import streamlit as st
import os
import time
from google import genai
from google.genai import types
import streamlit.components.v1 as components # 👈 ĐÃ THÊM: Import component để chèn HTML an toàn

# ==================== 🎨 CSS TÙY CHỈNH GIAO DIỆN CHUYÊN NGHIỆP VÀ TỐI GIẢN ====================
st.markdown("""
<style>

/* ===================== 🌟 BANNER TRÀN FULL MÀN HÌNH ===================== */

/* XÓA MARGIN/PADDING MẶC ĐỊNH CỦA STREAMLIT ĐỂ BANNER SÁT ĐẦU TRANG */
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

/* Banner full width nằm sát mép trên */
.custom-top-banner-wrapper {
    position: relative;
    width: 100vw;        /* Tràn 100% chiều ngang thực */
    left: 50%;
    right: 50%;
    margin-left: -50vw;  /* Kéo ra khỏi container của Streamlit */
    margin-right: -50vw;

    background: linear-gradient(90deg, #005CFF, #003EA8);
    text-align: center;
    padding: 34px 0 38px 0;   /* Thay bằng padding theo ý Thầy */
    box-shadow: 0 2px 12px rgba(0,0,0,0.18);

    margin-top: 0 !important;   /* đảm bảo sát mép trên */
}

/* Dòng tiêu đề chính */
.custom-top-banner-title {
    color: white;
    font-weight: 800;
    font-size: 2.3em;
    letter-spacing: 0.5px;
}

/* Dòng mô tả phụ */
.custom-top-banner-sub {
    color: #e9f0ff;
    margin-top: -4px;
    font-size: 1.15em;
    font-weight: 300;
}

/* ===================== 🎨 NỀN & BỐ CỤC TỔNG THỂ ===================== */
[data-testid="stAppViewContainer"] {
    background-color: #F4F7FF;   /* ⭐ Nền xanh nhạt rất dễ nhìn */
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
    background: white;
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
    background: #F6F8FF;
    border-left: 4px solid #003EA8;
}

/* ===================== ✏️ Ô GỬI TIN NHẮN ===================== */
[data-testid="stChatInput"] {
    background-color: #ffffff;
    border-radius: 14px;
    padding: 12px;
    border-top: 2px solid #dfe6ff;
    box-shadow: 0 -3px 10px rgba(0,0,0,0.05);
}
[data-testid="stChatInput"] button {
    background: #005CFF !important;
    color: white !important;
    border-radius: 8px;
    font-weight: 600;
}
[data-testid="stChatInput"] button:hover {
    background: #0048D6 !important;
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

if prompt := st.chat_input("💬 Gõ câu hỏi của bạn tại đây..."):

    # 🎯 LẤY NGÀY GIỜ THỰC TẾ TỪ HỆ THỐNG
    real_time = datetime.now().strftime("Hôm nay là ngày %d tháng %m năm %Y, Thứ %A.")

    # 🎯 CHÈN THÔNG ĐIỆP ÉP BUỘC AI LUÔN DÙNG NGÀY THỰC
    system_time_note = (
        "LƯU Ý CHO MÔ HÌNH: Đây là ngày giờ thực tế của hệ thống máy chủ: "
        + real_time +
        ". Khi học sinh hỏi về ngày tháng hoặc thời gian, bạn **PHẢI** dùng đúng thông tin này "
        "và **KHÔNG ĐƯỢC** tự suy đoán hoặc sử dụng ngày khác."
    )

    contents = [
        types.Part(text=system_time_note),
        types.Part(text=prompt)              # 📌 Prompt của học sinh
    ]


    if image_part:
        contents.insert(0, image_part)
        with st.chat_message("Học sinh"):
            st.markdown(f"<span class='chat-icon'>👩‍🎓</span>**Bài tập đính kèm:**", unsafe_allow_html=True)
            st.image(image_bytes, width=180)
            st.markdown(prompt)
    else:
        with st.chat_message("Học sinh"):
            st.markdown(f"<span class='chat-icon'>👩‍🎓</span>{prompt}", unsafe_allow_html=True)

    with st.spinner("⏳ Thầy Chánh đang suy nghĩ..."):
        response = st.session_state.chat_session.send_message(contents)

# Hiệu ứng “gõ chữ dần dần”
    with st.chat_message("Thầy Chánh"):
        placeholder = st.empty()
        text_display = ""
        for char in response.text:
            text_display += char
            # ĐÃ SỬA: Xóa dấu '}' thừa
            placeholder.markdown(f"<span class='chat-icon'>🤖</span>{text_display}", unsafe_allow_html=True) 
            time.sleep(0.008)  # tốc độ gõ (nhanh hơn một chút)
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















