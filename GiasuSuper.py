import streamlit as st
import os
import time
from google import genai
from google.genai import types

# ==================== 🎨 CSS TÙY CHỈNH GIAO DIỆN MỚI ====================
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
/* Ẩn tiêu đề hướng dẫn tải ảnh cũ */
st.markdown("📚 **Nhập câu hỏi hoặc tải ảnh bài tập để được hướng dẫn chi tiết:**") {
    display: none;
}

/* ----------- Hộp chat ----------- */
.stChatMessage {
    border-radius: 12px; 
    padding: 12px 18px;
    margin: 10px 0;
    line-height: 1.6;
    font-size: 1.0em;
    box-shadow: none; 
    border: 1px solid #f0f0f0; 
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
    border-left: 3px solid #0056b3; 
}

/* ----------- Biểu tượng chat ----------- */
.chat-icon {
    font-size: 20px;
    margin-right: 8px;
    vertical-align: top; 
}

/* ==================== VÙNG CHAT INPUT CỐ ĐỊNH ==================== */
/* Cố định container chứa chat input và file uploader */
.fixed-chat-container {
    position: fixed;
    bottom: 50px; /* Nằm ngay trên footer */
    left: 0;
    width: 100%;
    background-color: #ffffff;
    padding: 10px 15px;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.05); 
    z-index: 9999;
}
/* Điều chỉnh khoảng cách cuộn cho nội dung chính để tránh bị che */
[data-testid="stVerticalBlock"] {
    padding-bottom: 120px; /* Đảm bảo lịch sử chat luôn hiển thị trên thanh input */
}

/* ----------- Tùy chỉnh NÚT ĐÍNH KÈM (+) ----------- */
/* Ẩn toàn bộ File Uploader mặc định */
.stFileUploader {
    display: none; 
}
/* Tạo nút '+' lớn */
.custom-upload-button {
    background-color: #007bff; 
    border: none;
    color: white;
    font-size: 24px;
    font-weight: 700;
    border-radius: 50%; /* Hình tròn */
    width: 40px;
    height: 40px;
    line-height: 40px;
    text-align: center;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 123, 255, 0.4);
    transition: background-color 0.2s;
    /* Căn chỉnh vào giữa */
    margin-top: 10px; 
}
.custom-upload-button:hover {
    background-color: #0056b3;
}

/* Tùy chỉnh chat input để hòa hợp */
[data-testid="stChatInput"] {
    background-color: #f0f0f0; /* Màu nền xám nhạt */
    border-radius: 12px;
    box-shadow: none; 
    padding: 5px;
    margin: 5px 0 5px 0;
}
/* Bỏ padding dưới cùng của container chat input */
[data-testid="stChatInput"] > div:last-child {
    padding-bottom: 0px;
}

/* ----------- NÚT VỀ TRANG CHỦ CỐ ĐỊNH (Home Button) ----------- */
.home-button-container {
    position: fixed;
    bottom: 100px; /* Đặt phía trên fixed-chat-container */
    right: 20px;
    z-index: 1000000; 
}
.home-button-container a {
    text-decoration: none;
    display: inline-block;
    background-color: #007bff; 
    color: white;
    padding: 10px 18px;
    border-radius: 12px;
    font-weight: 600;
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
    transition: background-color 0.3s, transform 0.2s;
}
.home-button-container a:hover {
    background-color: #0056b3;
    transform: translateY(-2px);
}
.home-button-container a:active {
    transform: translateY(0);
}


/* ----------- Spinner & Footer giữ nguyên ----------- */
.stSpinner > div {
    color: #0066cc;
    font-weight: 700;
}
footer {visibility: hidden;}
.custom-footer-container {
    position: fixed;
    bottom: 0px;
    left: 0;
    width: 100%;
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
        system_instruction="Bạn là Thầy Chánh - Gia Sư AI THCS thân thiện, giúp học sinh lớp 6–9 học tất cả các môn. Bạn phải luôn xưng là 'Thầy' hoặc 'Thầy Chánh' khi giao tiếp. Giải thích dễ hiểu, có ví dụ cụ thể.",
        temperature=1
    )
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=config
    )

# ==================== 🧠 GIAO DIỆN NGƯỜI DÙNG ====================
st.title("🎓 Trợ lý AI - Hỗ trợ Học Tập - Thầy Chánh")
st.caption("Xin chào 👋 Tôi là **Trợ lý AI do thầy Mai Thiện Chánh tạo ra** – Hãy gửi câu hỏi hoặc hình bài tập, tôi sẽ giúp bạn học thật hiệu quả!")

# NÚT VỀ TRANG CHỦ CỐ ĐỊNH
st.markdown("""
<div class="home-button-container">
    <a href="https://dayhoctichcuc.netlify.app/" target="_self">
        🏠 Về trang chủ
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==================== 🕐 HIỂN THỊ LỊCH SỬ CHAT ====================
for msg in st.session_state.chat_session.get_history():
    role = "Thầy Chánh" if msg.role == "model" else "Học sinh"
    icon = "🤖" if role == "Thầy Chánh" else "👩‍🎓"
    with st.chat_message(role):
        st.markdown(f"<span class='chat-icon'>{icon}</span>{msg.parts[0].text}", unsafe_allow_html=True)

# ==================== VÙNG CHAT INPUT VÀ FILE UPLOADER CỐ ĐỊNH ====================
# Bọc cả hai trong một container cố định (fixed-chat-container)
st.markdown('<div class="fixed-chat-container">', unsafe_allow_html=True)

# Sử dụng st.columns để đặt nút (+) và ô nhập liệu cạnh nhau
col_upload, col_input = st.columns([1, 10])

with col_upload:
    # 1. Widget File Uploader THẬT (được ẩn bằng CSS)
    # Đây là widget được kích hoạt khi click vào nút giả (dấu '+')
    uploaded_file = st.file_uploader(
        "📸 Tải ảnh", 
        type=["png", "jpg", "jpeg"],
        key="file_uploader_key",
        label_visibility="collapsed"
    )
    # 2. Tạo Nút Giả (dấu '+') bằng HTML/Markdown
    # Nút này dùng JavaScript để click vào File Uploader thật
    st.markdown("""
    <label for="file_uploader_key-input" class="custom-upload-button">
        +
    </label>
    <script>
        // Lấy nút '+' giả
        const customButton = document.querySelector('.custom-upload-button');
        // Lấy nút 'Browse files' thật của st.file_uploader
        // Streamlit gán ID dựa trên key, ta cần tìm ID/tên class chính xác
        const realInput = document.getElementById('file_uploader_key-input');
        
        if (customButton && realInput) {
            customButton.addEventListener('click', () => {
                // Kích hoạt click vào input file thật
                realInput.click();
            });
        }
    </script>
    """, unsafe_allow_html=True)

# Xử lý tệp đã tải lên
image_part, image_bytes = None, None
if uploaded_file:
    image_bytes = uploaded_file.read()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_file.type)
    st.sidebar.image(image_bytes, caption='Ảnh bài tập đã tải', width=250)
    st.toast("✅ Ảnh đã tải thành công!", icon='📸')


with col_input:
    # Chat Input
    prompt = st.chat_input("💬 Gõ câu hỏi của bạn tại đây...", key="chat_input_main")

st.markdown('</div>', unsafe_allow_html=True) # Kết thúc fixed-chat-container

# ==================== ✍️ XỬ LÝ CHAT ====================
if prompt:
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
            time.sleep(0.008)  # tốc độ gõ 
        st.session_state.last_response = response.text

# ==================== 🧾 FOOTER ====================
st.markdown("""
<div class="custom-footer-container">
    © 2025 Gia Sư AI THCS – Phát triển bởi Thầy Chánh | Trường THCS Đức Phú, Lâm Đồng
</div>
""", unsafe_allow_html=True)
