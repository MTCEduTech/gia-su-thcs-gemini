import streamlit as st
import os
import time
from google import genai
from google.genai import types

# ==================== 🎨 CSS TÙY CHỈNH GIAO DIỆN CUỐI CÙNG (FIXED INPUT) ====================
st.markdown("""
<style>
/* ----------- Tổng thể (Quay lại màu xanh nhạt ban đầu) ----------- */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e8f0ff 0%, #f8fbff 100%); 
    font-family: "Segoe UI", sans-serif;
}

/* ----------- Tiêu đề & Hộp chat (Giữ nguyên cấu trúc ban đầu) ----------- */
h1 { color: #003366; text-align: center; font-weight: 700; margin-bottom: 0.2em; padding-top: 10px; }
[data-testid="stCaption"] { text-align: center; color: #444; font-size: 1.05em; }
.stChatMessage { border-radius: 16px; padding: 10px 18px; margin: 8px 0; line-height: 1.5; font-size: 1.05em; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.stChatMessage[data-testid="stChatMessageUser"] { background-color: #d8ecff; border: 1px solid #b5d6ff; }
.stChatMessage[data-testid="stChatMessageAssistant"] { background-color: #f2f5ff; border: 1px solid #dce3ff; }
.chat-icon { font-size: 22px; margin-right: 8px; vertical-align: middle; }
hr { border-top: 1px solid #eeeeee; margin: 1.5rem 0; }

/* Ẩn tiêu đề hướng dẫn tải ảnh cũ */
[data-testid="stVerticalBlock"] > div > :nth-child(3) { display: none; }
/* Ẩn File Uploader cũ (chúng ta sẽ dùng nó để tiêm nút '+' vào st.chat_input) */
.stFileUploader { display: none; }

/* ==================== FIX SCROLLING ==================== */
/* Thêm padding dưới cùng cho nội dung chính để tránh bị thanh input cố định che mất */
.main > div {
    padding-bottom: 90px; 
}
/* Đảm bảo thanh chat input luôn ở dưới cùng */
[data-testid="stChatInput"] {
    position: relative; /* Cần cho position: absolute của nút + */
    /* Di chuyển input text sang phải để nhường chỗ cho nút + */
    padding-left: 45px; 
}

/* ----------- NÚT '+' TIÊM VÀO CHAT INPUT ----------- */
.custom-upload-button-injected {
    position: absolute;
    top: 50%;
    left: 8px; /* Vị trí bên trái ô nhập */
    transform: translateY(-50%);
    background-color: #007bff;
    color: white;
    font-size: 20px;
    font-weight: 700;
    border-radius: 50%; 
    width: 30px;
    height: 30px;
    line-height: 30px;
    text-align: center;
    cursor: pointer;
    z-index: 10000; /* Đảm bảo nổi trên input */
}

/* ----------- NÚT VỀ TRANG CHỦ CỐ ĐỊNH SÁT DƯỚI ----------- */
.home-button-container {
    position: fixed;
    bottom: 50px; /* SÁT DƯỚI CÙNG */
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

# Khởi tạo session state cho file upload
if 'uploaded_file_data' not in st.session_state:
    st.session_state.uploaded_file_data = None


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


# ==================== 1. FILE UPLOADER ẨN ====================
# Phải đặt Uploader ở đây để nó tồn tại trong DOM và có thể được JS kích hoạt
# CSS đã ẩn hoàn toàn widget này
st.file_uploader(
    "📸 Tải ảnh", 
    type=["png", "jpg", "jpeg"],
    key="file_uploader_key",
    label_visibility="collapsed"
)

# ==================== 2. CHAT INPUT CỐ ĐỊNH ====================
# Streamlit tự động cố định widget này
prompt = st.chat_input("💬 Gõ câu hỏi của bạn tại đây...", key="chat_input_main")


# ==================== 3. JS INJECTION VÀ LOGIC XỬ LÝ FILE ====================
# JS Tiêm nút '+' vào st.chat_input và xử lý tệp
st.markdown("""
<div id="js_injection_point"></div>
<script>
    (function() {
        const uploaderInput = document.querySelector('[data-testid="stFileUploaderDropzone"] input[type="file"]');
        const chatInputContainer = document.querySelector('[data-testid="stChatInput"]');
        const injectionPoint = document.getElementById('js_injection_point');

        if (uploaderInput && chatInputContainer) {
            // Chỉ tiêm một lần (kiểm tra xem nút đã tồn tại chưa)
            if (!chatInputContainer.querySelector('.custom-upload-button-injected')) {
                const plusButton = document.createElement('div');
                plusButton.className = 'custom-upload-button-injected';
                plusButton.innerHTML = '+';

                // Gắn sự kiện click vào nút '+' giả
                plusButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    uploaderInput.click(); // Kích hoạt click vào input file thật
                });

                // Tiêm nút '+' vào container của chat input
                chatInputContainer.appendChild(plusButton);
            }
            // Xóa điểm tiêm tạm thời (nếu có)
            if (injectionPoint) {
                injectionPoint.remove();
            }
        }
    })();
</script>
""", unsafe_allow_html=True)


# ==================== 4. XỬ LÝ CHAT ====================
# Logic xử lý File Uploader: Lưu file data vào session state khi nó được upload
if st.session_state.file_uploader_key:
    try:
        uploaded_file = st.session_state.file_uploader_key
        # Kiểm tra nếu file đã được xử lý và lưu rồi
        if st.session_state.uploaded_file_data is None or st.session_state.uploaded_file_data['name'] != uploaded_file.name:
            image_bytes = uploaded_file.read()
            image_part = types.Part.from_bytes(data=image_bytes, mime_type=uploaded_file.type)
            
            # Lưu dữ liệu cần thiết vào session state
            st.session_state.uploaded_file_data = {
                'bytes': image_bytes,
                'part': image_part,
                'name': uploaded_file.name
            }
            st.toast(f"✅ Ảnh '{uploaded_file.name}' đã sẵn sàng gửi!", icon='📸')
            # Chạy lại để cập nhật giao diện (hiển thị toast)
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Lỗi xử lý tệp: {e}")
        st.session_state.file_uploader_key = None 
        st.session_state.uploaded_file_data = None


# Xử lý khi người dùng nhấn Enter/Gửi (prompt is not None)
if prompt:
    contents = [prompt]
    is_image_attached = st.session_state.uploaded_file_data is not None

    if is_image_attached:
        image_bytes_to_send = st.session_state.uploaded_file_data['bytes']
        image_part_to_send = st.session_state.uploaded_file_data['part']
        
        contents.insert(0, image_part_to_send)
        
    # HIỂN THỊ TIN NHẮN CỦA HỌC SINH
    with st.chat_message("Học sinh"):
        if is_image_attached:
            st.markdown(f"<span class='chat-icon'>👩‍🎓</span>**Bài tập đính kèm:**", unsafe_allow_html=True)
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
        
    # Sau khi gửi, xóa dữ liệu ảnh đã đính kèm khỏi session state
    st.session_state.file_uploader_key = None
    st.session_state.uploaded_file_data = None
    # Chạy lại script để xóa prompt khỏi ô nhập liệu và cập nhật giao diện
    st.experimental_rerun()


# ==================== 🧾 FOOTER ====================
st.markdown("""
<div class="custom-footer-container">
    © 2025 Gia Sư AI THCS – Phát triển bởi Thầy Chánh | Trường THCS Đức Phú, Lâm Đồng
</div>
""", unsafe_allow_html=True)

