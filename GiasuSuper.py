import streamlit as st
import os
import time
from google import genai
from google.genai import types
import streamlit.components.v1 as components # 👈 ĐÃ THÊM: Import component để chèn HTML an toàn

# ==================== 🎨 CSS TÙY CHỈNH GIAO DIỆN CHUYÊN NGHIỆP VÀ TỐI GIẢN ====================
st.markdown("""
<style>
/* ----------- Tổng thể ----------- */
[data-testid="stAppViewContainer"] {
    /* Nền hoàn toàn trắng (tối giản, chuyên nghiệp nhất) */
    background-color: #ffffff; 
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #333333;
}

/* ----------- Tiêu đề ----------- */
h1 {
    color: #003366; /* Xanh Navy đậm, uy tín */
    text-align: center;
    font-weight: 800; 
    margin-bottom: 0.2em;
    padding-top: 10px;
}
[data-testid="stCaption"] {
    text-align: center;
    color: #555555;
    font-size: 1.0em;
    font-style: italic;
}

/* ----------- Đường ngăn cách ----------- */
hr {
    border-top: 1px solid #eeeeee; /* Đường kẻ rất mỏng và nhạt */
    margin: 1.5rem 0;
}
st.markdown("📚 **Nhập câu hỏi hoặc tải ảnh bài tập để được hướng dẫn chi tiết:**") {
    font-weight: 600;
    color: #004080;
}

/* ----------- Hộp chat ----------- */
.stChatMessage {
    border-radius: 12px; /* Góc bo vừa phải */
    padding: 12px 18px;
    margin: 10px 0;
    line-height: 1.6;
    font-size: 1.0em;
    box-shadow: none; /* Bỏ bóng để tối giản */
    border: 1px solid #f0f0f0; /* Thêm border nhẹ thay cho bóng */
}
/* Tin nhắn Học sinh (User) - Nền trắng, chữ đen, nổi bật bên phải */
.stChatMessage[data-testid="stChatMessageUser"] {
    background-color: #ffffff; 
    color: #222222;
    margin-left: 20%; 
    border-left: 3px solid #007bff; /* Thanh màu xanh nổi bật */
}
/* Tin nhắn Thầy Chánh (Assistant) - Nền xám nhạt, chữ đen, nổi bật bên trái */
.stChatMessage[data-testid="stChatMessageAssistant"] {
    background-color: #f7f7f7; /* Nền xám nhạt */
    color: #333333;
    margin-right: 20%; 
    border-left: 3px solid #0056b3; /* Thanh màu xanh đậm hơn */
}

/* ----------- Biểu tượng chat ----------- */
.chat-icon {
    font-size: 20px;
    margin-right: 8px;
    vertical-align: top; 
}

/* ----------- File upload ----------- */
.stFileUploader {
    border: 2px dashed #cccccc; /* Border xám trung tính */
    border-radius: 12px;
    background-color: #fcfcfc; 
    padding: 15px;
    margin-bottom: 20px;
}
.stFileUploader:hover {
    background-color: #f9f9f9;
    border-color: #aaaaaa;
}

/* ----------- Thanh nhập chat ----------- */
[data-testid="stChatInput"] {
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 -4px 15px rgba(0,0,0,0.05); /* Bóng nhẹ dưới cùng */
    padding: 10px;
}
/* Nút Gửi */
[data-testid="stChatInput"] button {
    background-color: #0066cc; 
    border-radius: 8px;
}
[data-testid="stChatInput"] button:hover {
    background-color: #005bb5;
}

/* ----------- Spinner ----------- */
.stSpinner > div {
    color: #0066cc;
    font-weight: 700;
}

/* ----------- Footer ----------- */
footer {visibility: hidden;}
.custom-footer-container {
    position: fixed;
    bottom: 0px;
    left: 0;
    width: 100%;
    /* Màu xanh đậm đơn sắc cho sự ổn định */
    background-color: #004d99; 
    padding: 8px 0;
    text-align: center;
    font-size: 0.85em;
    color: white;
    z-index: 999999;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.15);
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
st.title("🎓 GIA SƯ AI 24/7 - Hỗ trợ Học Tập")
st.caption("Xin chào 👋 Tôi là **Trợ lý AI do thầy Mai Thiện Chánh tạo ra** – Hãy gửi câu hỏi hoặc hình bài tập, tôi sẽ giúp bạn học thật hiệu quả!")

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
    © 2025 Gia Sư AI THCS – Phát triển bởi Thầy Chánh | Trường THCS Đức Phú, Lâm Đồng || <a href="https://dayhoctichcuc.netlify.app/" target="_blank" class="home-button-link" style="color: white; text-decoration: none;">
            🏠 Về trang chủ BỘ CÔNG CỤ DẠY HỌC TÍCH CỰC
        </a>
</div>
""", unsafe_allow_html=True)








