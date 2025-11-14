import streamlit as st
import os
import time
from google import genai
from google.genai import types

# ==================== 🎨 CSS TÙY CHỈNH GIAO DIỆN CUỐI CÙNG (FIXED INPUT) ====================
st.markdown("""
<style>
/* ----------- Tổng thể ----------- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f0ff 0%, #f8fbff 100%); 
    font-family: "Segoe UI", sans-serif;
}

/* ----------- Tiêu đề & Hộp chat ----------- */
h1 { color: #003366; text-align: center; font-weight: 700; margin-bottom: 0.2em; padding-top: 10px; }
[data-testid="stCaption"] { text-align: center; color: #444; font-size: 1.05em; }
.stChatMessage { border-radius: 16px; padding: 10px 18px; margin: 8px 0; line-height: 1.5; font-size: 1.05em; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.stChatMessage[data-testid="stChatMessageUser"] { background-color: #d8ecff; border: 1px solid #b5d6ff; }
.stChatMessage[data-testid="stChatMessageAssistant"] { background-color: #f2f5ff; border: 1px solid #dce3ff; }
.chat-icon { font-size: 22px; margin-right: 8px; vertical-align: middle; }
hr { border-top: 1px solid #eeeeee; margin: 1.5rem 0; }

/* Ẩn tiêu đề hướng dẫn tải ảnh và File Uploader mặc định */
.stFileUploader { display: none; }
[data-testid="stVerticalBlock"] > div > :nth-child(3) { display: none; }


/* ==================== VÙNG CHAT INPUT CỐ ĐỊNH ==================== */
/* Container bao bọc Input và Nút gửi */
.fixed-chat-container {
    position: fixed;
    bottom: 50px; /* Nằm ngay trên footer */
    left: 0;
    width: 100%;
    background-color: #ffffff;
    padding: 10px 15px;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.05); 
    z-index: 9999;
    /* Dùng Flex để căn chỉnh các cột */
    display: flex;
    align-items: center;
    gap: 10px;
    padding-left: 15px;
    padding-right: 15px;
}
/* Điều chỉnh khoảng cách cuộn cho nội dung chính (Fixed Scrolling) */
.main > div {
    padding-bottom: 120px; 
}


/* ----------- NÚT '+' ĐÍNH KÈM TỆP (Custom Button) ----------- */
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

/* ----------- NÚT GỬI (Send Button) ----------- */
.stButton button {
    background-color: #007bff;
    color: white;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    padding: 0;
    line-height: 40px;
    font-size: 20px;
    font-weight: bold;
    box-shadow: 0 2px 5px rgba(0, 123, 255, 0.4);
    transition: background-color 0.2s;
    margin-top: 0px;
}
.stButton button:hover {
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


/* ----------- Footer giữ nguyên ----------- */
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
        system_instruction="Bạn là Thầy Chánh - Gia Sư AI THCS thân thiện, giúp học sinh lớp 6–9 học tất cả các môn. Bạn phải luôn xưng là 'Thầy' hoặc 'Thầy Chánh' khi giao tiếp. Giải thích dễ hiểu, có ví dụ cụ thể.",
        temperature=1
    )
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=config
    )

# Khởi tạo session state cho file upload và prompt
if 'uploaded_file_data' not in st.session_state:
    st.session_state.uploaded_file_data = None
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""


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


# ==================== LOGIC XỬ LÝ FILE UPLOADER (Callback) ====================
def handle_file_upload_change():
    uploaded_file = st.session_state.file_uploader_key
    if uploaded_file is not None:
        try:
            # Đọc bytes và Part
            image_bytes = uploaded_file.read()
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_file.type)
            
            # Lưu dữ liệu cần thiết vào session state
            st.session_state.uploaded_file_data = {
                'bytes': image_bytes,
                'part': image_part,
                'name': uploaded_file.name
            }
            st.toast(f"✅ Ảnh '{uploaded_file.name}' đã sẵn sàng gửi!", icon='📸')
            
            # Xóa file khỏi file_uploader_key để chuẩn bị cho lần upload tiếp theo
            st.session_state.file_uploader_key = None
            st.experimental_rerun() # Rerun để hiển thị toast

        except Exception as e:
            st.error(f"Lỗi xử lý tệp: {e}")
            st.session_state.uploaded_file_data = None


# ==================== VÙNG CHAT INPUT CỐ ĐỊNH (Sử dụng st.container và st.columns) ====================
# Bọc các thành phần input trong một container để áp dụng CSS fixed
st.markdown('<div class="fixed-chat-container">', unsafe_allow_html=True)

# 1. Widget File Uploader THẬT (bị ẩn bởi CSS)
# Phải đặt Uploader ở đây để nó tồn tại trong DOM và có thể được JS kích hoạt
uploaded_file_widget = st.file_uploader(
    "📸 Tải ảnh", 
    type=["png", "jpg", "jpeg"],
    key="file_uploader_key",
    label_visibility="collapsed",
    on_change=handle_file_upload_change
)

# 2. Tạo cột cho Nút +, Ô nhập liệu và Nút Gửi
col_upload, col_input, col_send = st.columns([1, 8, 1]) 

with col_upload:
    # Nút "+" giả bằng HTML/Markdown
    st.markdown("""
    <label for="file_uploader_key-input" class="custom-upload-button">
        +
    </label>
    <script>
        // Hàm JS để kích hoạt Uploader
        (function() {
            const customButton = document.querySelector('.custom-upload-button');
            // Tìm input file thật (nằm trong stFileUploaderDropzone)
            const realInput = document.querySelector('[data-testid="stFileUploaderDropzone"] input[type="file"]');
            
            if (customButton && realInput) {
                customButton.addEventListener('click', (e) => {
                    e.preventDefault(); 
                    realInput.click(); // Kích hoạt click vào input file thật
                });
            }
        })();
    </script>
    """, unsafe_allow_html=True)

with col_input:
    # Ô nhập liệu (Text Input)
    st.text_input("💬 Gõ câu hỏi của bạn tại đây...", 
                   key="user_prompt", 
                   label_visibility="collapsed")
    
with col_send:
    # Nút Gửi (Submit Button)
    st.button("➤", key="send_button", help="Gửi câu hỏi")


st.markdown('</div>', unsafe_allow_html=True)


# ==================== LOGIC XỬ LÝ CHAT (Khi nút gửi được nhấn) ====================
if st.session_state.send_button and st.session_state.user_prompt:
    prompt = st.session_state.user_prompt
    contents = [prompt]
    is_image_attached = st.session_state.uploaded_file_data is not None

    # Lấy dữ liệu ảnh nếu có
    image_bytes_to_send = None
    if is_image_attached:
        image_bytes_to_send = st.session_state.uploaded_file_data['bytes']
        image_part_to_send = st.session_state.uploaded_file_data['part']
        contents.insert(0, image_part_to_send)
        
    # HIỂN THỊ TIN NHẮN CỦA HỌC SINH
    with st.chat_message("Học sinh"):
        if is_image_attached:
            st.markdown(f"<span class='chat-icon'>👩‍🎓</span>**Bài tập đính kèm:**", unsafe_allow_html=True)
            if image_bytes_to_send:
                st.image(image_bytes_to_send, width=180)
        st.markdown(prompt)

    # GỬI TỚI GEMINI
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
        
    # Sau khi gửi, xóa dữ liệu ảnh và prompt để làm sạch giao diện
    st.session_state.uploaded_file_data = None
    st.session_state.user_prompt = "" 
    st.experimental_rerun() # Rerun để làm sạch ô nhập liệu

# ==================== 🧾 FOOTER ====================
st.markdown("""
<div class="custom-footer-container">
    © 2025 Gia Sư AI THCS – Phát triển bởi Thầy Chánh | Trường THCS Đức Phú, Lâm Đồng
</div>
""", unsafe_allow_html=True)
