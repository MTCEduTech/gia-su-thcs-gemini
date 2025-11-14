import streamlit as st
import os
import time
from google import genai
from google.genai import types

# ==================== 🎨 CSS TÙY CHỈNH GIAO DIỆN CUỐI CÙNG ====================
st.markdown("""
<style>
/* ----------- Tổng thể ----------- */
[data-testid="stAppViewContainer"] {
    background-color: #ffffff; 
    font-family: 'Inter', 'Segoe UI', sans-serif;
    color: #333333;
}

/* ----------- Tiêu đề & Caption ----------- */
h1 {
    color: #003366; 
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
hr { border-top: 1px solid #eeeeee; margin: 1.5rem 0; }

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
.stChatMessage[data-testid="stChatMessageUser"] {
    background-color: #ffffff; 
    color: #222222;
    margin-left: 20%; 
    border-left: 3px solid #007bff; 
}
.stChatMessage[data-testid="stChatMessageAssistant"] {
    background-color: #f7f7f7; 
    color: #333333;
    margin-right: 20%; 
    border-left: 3px solid #0056b3; 
}

/* ----------- VÙNG CHAT INPUT CỐ ĐỊNH (Sử dụng st.form) ----------- */
/* Cố định container chứa form và file uploader */
/* Dùng class của Streamlit để nhắm chính xác hơn */
.stApp [data-testid="stForm"] {
    position: fixed;
    bottom: 50px; /* Nằm ngay trên footer */
    left: 0;
    width: 100%;
    background-color: #ffffff;
    padding: 10px 15px;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.05); 
    z-index: 9999;
    /* Dùng Flexbox để căn chỉnh các cột trong form */
    display: flex;
    align-items: center;
    gap: 10px;
    /* Thêm khoảng đệm để không bị sát mép khi thu nhỏ */
    padding-left: 15px;
    padding-right: 15px;
}
/* Điều chỉnh khoảng cách cuộn cho nội dung chính để tránh bị che */
[data-testid="stVerticalBlock"] {
    padding-bottom: 120px; 
}

/* ----------- Tùy chỉnh DẤU + (File Uploader) ----------- */
/* 1. Ẩn toàn bộ File Uploader mặc định, chỉ để lại nút Browse (để JavaScript hoạt động) */
.stFileUploader {
    display: none; 
}
/* 2. Tạo nút '+' giả bằng HTML */
.custom-upload-button {
    background-color: #007bff; 
    border: none;
    color: white;
    font-size: 24px;
    font-weight: 700;
    border-radius: 50%; 
    width: 40px;
    height: 40px;
    line-height: 40px;
    text-align: center;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 123, 255, 0.4);
    transition: background-color 0.2s;
    margin-top: 0px; 
}
.custom-upload-button:hover {
    background-color: #0056b3;
}

/* ----------- NÚT VỀ TRANG CHỦ CỐ ĐỊNH SÁT DƯỚI ----------- */
.home-button-container {
    position: fixed;
    bottom: 0px; /* SÁT DƯỚI CÙNG */
    right: 0px;
    z-index: 1000001; /* Trên cả footer */
}
.home-button-container a {
    text-decoration: none;
    display: inline-block;
    background-color: #007bff; 
    color: white;
    /* Tăng padding để che một phần nút Manage app */
    padding: 10px 30px 10px 18px; 
    border-top-left-radius: 12px;
    border-bottom-right-radius: 0px;
    border-bottom-left-radius: 0px; 
    font-weight: 600;
    box-shadow: 0 0px 10px rgba(0, 123, 255, 0.4);
    transition: background-color 0.3s;
}
.home-button-container a:hover {
    background-color: #0056b3;
}

/* ----------- CÁC PHẦN KHÁC ----------- */
.stSpinner > div { color: #0066cc; font-weight: 700; }
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
st.caption("Xin chào 👋 Tôi là **Trợ lý AI do thầy Mai Thiện Chánh tạo ra** – hãy gửi câu hỏi hoặc hình bài tập, tôi sẽ giúp bạn học thật hiệu quả!")

# NÚT VỀ TRANG CHỦ CỐ ĐỊNH SÁT DƯỚI
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

# ==================== VÙNG CHAT INPUT & UPLOADER CỐ ĐỊNH (Dùng st.form) ====================
# Đặt form ở cuối file, Streamlit sẽ tự động cố định nó theo CSS đã định nghĩa
with st.form(key='chat_form', clear_on_submit=True):
    
    # 1. Widget File Uploader THẬT (bị ẩn bởi CSS)
    # Phải đặt Uploader trước để JS dễ dàng tìm thấy nó trong DOM
    uploaded_file = st.file_uploader(
        "📸 Tải ảnh", 
        type=["png", "jpg", "jpeg"],
        key="file_uploader_key",
        label_visibility="collapsed"
    )
    
    # Dùng st.columns để căn chỉnh nút "+" và ô nhập liệu
    col_upload, col_input, col_send = st.columns([1, 8, 1]) 
    
    with col_upload:
        # Tạo Nút Giả (dấu '+') bằng HTML/Markdown
        # Nút này dùng JavaScript để kích hoạt File Uploader ẩn
        st.markdown("""
        <label for="file_uploader_key-input" class="custom-upload-button">
            +
        </label>
        <script>
            // HÀM JS ĐỂ KÍCH HOẠT UPLOADER
            (function() {
                // Lấy nút '+' giả
                const customButton = document.querySelector('.custom-upload-button');
                // Lấy input file thật (nằm trong stFileUploaderDropzone)
                const realInput = document.querySelector('[data-testid="stFileUploaderDropzone"] input[type="file"]');
                
                if (customButton && realInput) {
                    customButton.addEventListener('click', (e) => {
                        e.preventDefault(); // Ngăn chặn form submit ngay lập tức
                        realInput.click(); // Kích hoạt click vào input file thật
                    });
                }
            })();
        </script>
        """, unsafe_allow_html=True)

    # 2. Ô nhập liệu (Text Input)
    with col_input:
        prompt = st.text_input("💬 Gõ câu hỏi của bạn tại đây...", 
                               key="text_input_main", 
                               label_visibility="collapsed")
    
    # 3. Nút Gửi (Submit)
    with col_send:
        # Nút submit là bắt buộc trong form
        st.form_submit_button("➤", key="submit_button_key", disabled=(not prompt and not st.session_state.file_uploader_key)) 


# Xử lý tệp đã tải lên (Lưu vào session state để dùng cho lần gửi tiếp theo)
image_part, image_bytes = None, None
if 'file_uploader_key' in st.session_state and st.session_state.file_uploader_key:
    # Lấy file từ session state sau khi uploader được dùng
    uploaded_file_data = st.session_state.file_uploader_key
    image_bytes = uploaded_file_data.read()
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_file_data.type)
    # Hiển thị ảnh trong sidebar (tùy chọn)
    # st.sidebar.image(image_bytes, caption='Ảnh bài tập đã tải', width=250)


# ==================== XỬ LÝ CHAT SAU KHI FORM SUBMIT ====================
# Kiểm tra nếu form đã được submit
if st.session_state.submit_button_key:
    # Lấy prompt từ session state
    current_prompt = st.session_state.text_input_main
    
    # Tạo contents
    contents = [current_prompt if current_prompt else ""]
    is_image_attached = image_part is not None
    
    if is_image_attached:
        contents.insert(0, image_part)
        
    # HIỂN THỊ TIN NHẮN CỦA HỌC SINH
    with st.chat_message("Học sinh"):
        if is_image_attached:
            st.markdown(f"<span class='chat-icon'>👩‍🎓</span>**Bài tập đính kèm:**", unsafe_allow_html=True)
            st.image(image_bytes, width=180)
        st.markdown(current_prompt if current_prompt else "(Chỉ gửi ảnh)")

    # GỬI TỚI GEMINI
    if current_prompt or is_image_attached:
        with st.spinner("⏳ Thầy Chánh đang suy nghĩ..."):
            response = st.session_state.chat_session.send_message(contents)

        # HIỂN THỊ PHẢN HỒI CỦA THẦY CHÁNH
        with st.chat_message("Thầy Chánh"):
            placeholder = st.empty()
            text_display = ""
            for char in response.text:
                text_display += char
                placeholder.markdown(f"<span class='chat-icon'>🤖</span>{text_display}", unsafe_allow_html=True)
                time.sleep(0.008)
            st.session_state.last_response = response.text
            
    # Xóa file uploader sau khi gửi tin nhắn thành công để không gửi lại
    if 'file_uploader_key' in st.session_state:
        st.session_state.file_uploader_key = None 
        # Cần chạy lại script để cập nhật giao diện
        st.experimental_rerun()


# ==================== 🧾 FOOTER ====================
st.markdown("""
<div class="custom-footer-container">
    © 2025 Gia Sư AI THCS – Phát triển bởi Thầy Chánh | Trường THCS Đức Phú, Lâm Đồng
</div>
""", unsafe_allow_html=True)
