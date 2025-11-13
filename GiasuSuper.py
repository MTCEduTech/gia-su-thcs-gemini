import streamlit as st
import os
import time
from google import genai
from google.genai import types

# ==================== 🎨 CSS TÙY CHỈNH GIAO DIỆN ====================
st.markdown("""
<style>
/* ----------- Tổng thể ----------- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f0ff 0%, #f8fbff 100%);
    font-family: "Segoe UI", sans-serif;
}

/* ----------- Tiêu đề ----------- */
h1 {
    color: #003366;
    text-align: center;
    font-weight: 700;
    margin-bottom: 0.2em;
}
[data-testid="stCaption"] {
    text-align: center;
    color: #444;
    font-size: 1.05em;
}

/* ----------- Hộp chat ----------- */
.stChatMessage {
    border-radius: 16px;
    padding: 10px 18px;
    margin: 8px 0;
    line-height: 1.5;
    font-size: 1.05em;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.stChatMessage[data-testid="stChatMessageUser"] {
    background-color: #d8ecff;
    border: 1px solid #b5d6ff;
}
.stChatMessage[data-testid="stChatMessageAssistant"] {
    background-color: #f2f5ff;
    border: 1px solid #dce3ff;
}

/* ----------- Biểu tượng chat ----------- */
.chat-icon {
    font-size: 22px;
    margin-right: 8px;
    vertical-align: middle;
}

/* ----------- File upload ----------- */
.stFileUploader {
    border: 2px dashed #99baff;
    border-radius: 12px;
    background-color: #f5f8ff;
}
.stFileUploader:hover {
    background-color: #eaf1ff;
}

/* ----------- Thanh nhập chat ----------- */
[data-testid="stChatInput"] {
    background-color: #ffffff;
    border-radius: 12px;
    box-shadow: 0 -2px 8px rgba(0,0,0,0.05);
}

/* ----------- Spinner ----------- */
.stSpinner > div {
    color: #0066cc;
    font-weight: 600;
}

/* ----------- Footer ----------- */
footer {visibility: hidden;}
.custom-footer-container {
    position: fixed;
    bottom: 0px;
    left: 0;
    width: 100%;
    background: linear-gradient(90deg, #004080, #0066cc);
    padding: 6px 0;
    text-align: center;
    font-size: 0.8em;
    color: white;
    z-index: 999999;
    box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
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

