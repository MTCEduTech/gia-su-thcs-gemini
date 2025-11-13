import streamlit as st
import os
import time
from google import genai
from google.genai import types

# ==================== 🎨 CSS TÙY CHỈNH GIAO DIỆN CHUYÊN NGHIỆP ====================
st.markdown("""
<style>
/* ----------- Tổng thể ----------- */
[data-testid="stAppViewContainer"] {
    /* Nền gradient nhẹ nhàng, chuyên nghiệp */
    background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
    font-family: 'Inter', 'Segoe UI', sans-serif; /* Font hiện đại hơn */
    color: #333333; /* Màu chữ chính */
}

/* ----------- Tiêu đề ----------- */
h1 {
    color: #004080; /* Màu xanh đậm, uy tín */
    text-align: center;
    font-weight: 800; /* Đậm hơn để nổi bật */
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
    border-top: 1px solid #e0e0e0;
    margin: 1.5rem 0;
}

/* ----------- Hộp chat ----------- */
.stChatMessage {
    border-radius: 18px; /* Bo góc mềm mại hơn */
    padding: 12px 20px;
    margin: 10px 0;
    line-height: 1.6;
    font-size: 1.0em;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* Đổ bóng tinh tế */
    transition: all 0.3s ease;
}
/* Tin nhắn Học sinh (User) */
.stChatMessage[data-testid="stChatMessageUser"] {
    background-color: #e6f7ff; /* Xanh nhạt tinh tế */
    border: none; /* Bỏ border để tối giản */
    color: #003366;
    margin-left: 20%; /* Dịch sang phải */
}
/* Tin nhắn Thầy Chánh (Assistant) */
.stChatMessage[data-testid="stChatMessageAssistant"] {
    background-color: #ffffff; /* Trắng sạch sẽ */
    border: 1px solid #e0e0e0;
    color: #333333;
    margin-right: 20%; /* Dịch sang trái */
}

/* ----------- Biểu tượng chat ----------- */
.chat-icon {
    font-size: 20px;
    margin-right: 8px;
    vertical-align: top; /* Căn chỉnh biểu tượng */
}

/* ----------- File upload ----------- */
.stFileUploader {
    border: 3px dashed #b3d9ff; /* Màu xanh dịu */
    border-radius: 15px;
    background-color: #f0f8ff; /* Nền xanh rất nhạt */
    padding: 15px;
    margin-bottom: 20px;
}
.stFileUploader:hover {
    background-color: #e3f2ff;
    border-color: #80bfff;
}

/* ----------- Thanh nhập chat ----------- */
[data-testid="stChatInput"] {
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 -4px 15px rgba(0,0,0,0.08); /* Bóng rõ hơn */
    padding: 10px;
}
/* Nút Gửi */
[data-testid="stChatInput"] button {
    background-color: #0066cc; /* Màu xanh dương chủ đạo */
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

/* ----------- Footer (Giữ nguyên phong cách chuyên nghiệp, thay màu hiện đại hơn) ----------- */
footer {visibility: hidden;}
.custom-footer-container {
    position: fixed;
    bottom: 0px;
    left: 0;
    width: 100%;
    /* Gradient footer tông xanh-xám chuyên nghiệp */
    background: linear-gradient(90deg, #004d99, #0066cc, #004d99);
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
        system_instruction="Bạn là Gia Sư AI THCS thân thiện, giúp học sinh lớp 6–9 học tất cả các môn. Giải thích dễ hiểu, có ví dụ cụ thể.",
        temperature=1
    )
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=config
    )

# ==================== 🧠 GIAO DIỆN NGƯỜI DÙNG ====================
st.title("🎓 Trợ lý AI - Hỗ trợ Học Tập - Thầy Chánh")
st.caption("Xin chào 👋 Tôi là **Trợ lý AI do thầy Mai Thiện Chánh tạo ra** – hãy gửi câu hỏi hoặc hình bài tập, tôi sẽ giúp bạn học thật hiệu quả!")

st.markdown("---")
st.markdown("📚 **Nhập câu hỏi hoặc tải ảnh bài tập để được hướng dẫn chi tiết:**")

uploaded_file = st.file_uploader("📸 Tải ảnh bài tập", type=["png", "jpg", "jpeg"])
image_part, image_bytes = None, None
if uploaded_file:
    image_bytes = uploaded_file.read()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_file.type)
    st.sidebar.image(image_bytes, caption='Ảnh bài tập đã tải', width=250)
    st.success("✅ Ảnh đã tải thành công!")

# ==================== 🕐 HIỂN THỊ LỊCH SỬ CHAT ====================
for msg in st.session_state.chat_session.get_history():
    role = "Thầy Chánh" if msg.role == "model" else "Học sinh"
    icon = "🤖" if role == "Thầy Chánh" else "👩‍🎓"
    with st.chat_message(role):
        st.markdown(f"<span class='chat-icon'>{icon}</span>{msg.parts[0].text}", unsafe_allow_html=True)

# ==================== ✍️ NHẬP CHAT ====================
if prompt := st.chat_input("💬 Gõ câu hỏi của bạn tại đây..."):
    contents = [prompt]
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
            placeholder.markdown(f"<span class='chat-icon'>🤖</span>{text_display}", unsafe_allow_html=True)
            time.sleep(0.008)  # tốc độ gõ (nhanh hơn một chút)
        st.session_state.last_response = response.text

# ==================== 🧾 FOOTER ====================
st.markdown("""
<div class="custom-footer-container">
    © 2025 Gia Sư AI THCS – Phát triển bởi Thầy Chánh | Trường THCS Đức Phú, Lâm Đồng
</div>
""", unsafe_allow_html=True)
