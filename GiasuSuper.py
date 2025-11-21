import streamlit as st
import os
import time
from google import genai
from google.genai import types
import streamlit.components.v1 as components
from datetime import datetime
from lunardate import LunarDate

# ==================== 🎨 CSS TÙY CHỈNH ====================
st.markdown("""
<style>
header, [data-testid="stHeader"] { display: none !important; }
.custom-top-banner-wrapper { position: relative; width: 100vw; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #87CEEB; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 130px; text-align: center; }
.custom-top-banner-title { color: blue; font-weight: 800; font-size: 2.3em; margin: 0; }
.custom-top-banner-sub { color: white; font-size: 1.15em; font-weight: 500; margin-top: 4px; }
[data-testid="stAppViewContainer"] { background-color: #87CEEB; font-family: 'Inter', sans-serif; color: #202020; }
.stChatMessage { border-radius: 14px; padding: 14px 20px; background: #FFFFFF; border: 1px solid #e0e6f5; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
[data-testid="stChatMessageUser"] { margin-left: 20%; border-left: 4px solid #006AFF; }
[data-testid="stChatMessageAssistant"] { margin-right: 20%; background: #87CEEB; border-left: 4px solid #003EA8; }
[data-testid="stChatInput"] { background-color: white; border-radius: 14px; padding: 12px; border-top: 2px solid #dfe6ff; box-shadow: 0 -3px 10px rgba(0,0,0,0.05); }
[data-testid="stChatInput"] button { background: #FFFFFF !important; color: blue !important; border-radius: 8px; font-weight: 600; }
.chat-icon { font-size: 20px; margin-right: 8px; }
.custom-footer-container { position: fixed; bottom: 0; left: 0; width: 100vw; background: #003EA8; padding: 12px 0; text-align: center; color: white; font-size: 0.9em; }
html, body, [data-testid="stAppViewContainer"] { padding-bottom: 90px !important; }
</style>
""", unsafe_allow_html=True)

# ==================== ⚙️ CLIENT GEMINI ====================
@st.cache_resource
def get_gemini_client():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("❌ Chưa có GEMINI_API_KEY")
        st.stop()

    return genai.Client(api_key=api_key)

client = get_gemini_client()

# ==================== ⚙️ CONFIG BAN ĐẦU ====================
if "chat_config" not in st.session_state:
    st.session_state.chat_config = types.GenerateContentConfig(
        system_instruction=(
            "Bạn là Thầy Chánh - Gia Sư AI THCS thân thiện. "
            "Luôn xưng 'Thầy' hoặc 'Thầy Chánh'. Giải thích rõ, dễ hiểu."
        ),
        temperature=1
    )

# ==================== ⚙️ TẠO PHIÊN CHAT ====================
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=st.session_state.chat_config
    )

# ==================== 🧠 GIAO DIỆN ====================
st.markdown("""
<div class="custom-top-banner-wrapper">
    <div class="custom-top-banner-title">🎓 GIA SƯ AI 24/7 – HỖ TRỢ HỌC TẬP</div>
    <div class="custom-top-banner-sub">Trợ lý học tập do Thầy Mai Thiện Chánh phát triển</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")
st.markdown("📚 **Nhập câu hỏi hoặc tải ảnh bài tập để được hướng dẫn chi tiết:**")

# ==================== 📤 UPLOAD ẢNH ====================
uploaded_file = st.file_uploader("📸 Tải ảnh bài tập", type=["png","jpg","jpeg"])
image_part, image_bytes = None, None

if uploaded_file:
    image_bytes = uploaded_file.read()
    image_part = types.Part.from_bytes(image_bytes, uploaded_file.type)
    st.sidebar.image(image_bytes, caption="Ảnh bài tập", width=250)

st.markdown("---")

# ==================== 🗑 XÓA LỊCH SỬ ====================
if st.button("🗑 Xóa toàn bộ lịch sử chat"):
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=st.session_state.chat_config
    )
    st.rerun()

# ==================== 🕐 HIỂN THỊ LỊCH SỬ ====================
for msg in st.session_state.chat_session.get_history():
    # ẨN SYSTEM MESSAGE
    if "LƯU Ý THỜI GIAN HỆ THỐNG" in msg.parts[0].text:
        continue

    role = "Thầy Chánh" if msg.role == "model" else "Học sinh"
    icon = "🤖" if msg.role == "model" else "👩‍🎓"

    try:
        text = msg.parts[0].text
    except:
        text = str(msg)

    with st.chat_message(role):
        st.markdown(f"<span class='chat-icon'>{icon}</span>{text}", unsafe_allow_html=True)

# ==================== ✍️ XỬ LÝ NGƯỜI DÙNG ====================
def can_chi_year(year):
    can = ["Giáp","Ất","Bính","Đinh","Mậu","Kỷ","Canh","Tân","Nhâm","Quý"]
    chi = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
    return f"{can[(year+6)%10]} {chi[(year+8)%12]}"

prompt = st.chat_input("💬 Gõ câu hỏi...")

if prompt:

    # 📌 Thời gian thật
    now = datetime.now()

    dl = f"Hôm nay là ngày {now.day}/{now.month}/{now.year}, Thứ {now.strftime('%A']}."
    lunar = LunarDate.fromSolarDate(now.year, now.month, now.day)
    am = f"Ngày {lunar.day} tháng {lunar.month} năm {can_chi_year(lunar.year)}."

    # 📌 Tạo system note (ẩn)
    system_note = (
        "LƯU Ý THỜI GIAN HỆ THỐNG:\n"
        + dl + "\n" + am +
        "\nLuôn dùng đúng các thông tin này khi trả lời về thời gian."
    )

    # Gửi system note — nhưng ẨN không hiển thị
    st.session_state.chat_session.send_message(
        [types.Part(text=system_note)]
    )

    # 📌 Hiển thị prompt của học sinh
    if image_part:
        with st.chat_message("Học sinh"):
            st.markdown("<span class='chat-icon'>👩‍🎓</span>**Bài tập đính kèm:**", unsafe_allow_html=True)
            st.image(image_bytes, width=200)
            st.markdown(prompt)
    else:
        with st.chat_message("Học sinh"):
            st.markdown(f"<span class='chat-icon'>👩‍🎓</span>{prompt}", unsafe_allow_html=True)

    # 📌 Chuẩn bị nội dung gửi lên Gemini
    contents = []
    if image_part:
        contents.append(image_part)
    contents.append(types.Part(text=prompt))

    # 📌 Gửi lên mô hình
    with st.spinner("⏳ Thầy Chánh đang suy nghĩ..."):
        response = st.session_state.chat_session.send_message(contents)

    # 📌 Hiển thị với hiệu ứng gõ chữ
    with st.chat_message("Thầy Chánh"):
        placeholder = st.empty()
        out = ""

        try:
            text = response.text
        except:
            text = str(response)

        for ch in text:
            out += ch
            placeholder.markdown(f"<span class='chat-icon'>🤖</span>{out}", unsafe_allow_html=True)
            time.sleep(0.008)

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



