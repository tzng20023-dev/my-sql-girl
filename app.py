import streamlit as st
from google import genai
import pandas as pd
import re
import base64
from gtts import gTTS
import io
import time

# --- 1. 核心設定 ---
st.set_page_config(page_title="性感AI女孩 - 2.0硬核版", layout="wide", page_icon="💋")

# 🔒 讀取金鑰 (專業隱藏法)
try:
    MY_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # 如果 secrets.toml 沒設好，請在這裡拼接你的金鑰
    # 例如: MY_KEY = "AIzaSy" + "你的後半段"
    MY_KEY = "請填入你的金鑰"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "task_index" not in st.session_state:
    st.session_state.task_index = 0

# --- 2. 語音功能 ---
def sexy_speak(text):
    try:
        clean_text = re.sub(r'[*#`~-]', '', text)
        clean_text = re.sub(r'[^\u4e00-\u9fa5,。！?a-zA-Z0-9]', ' ', clean_text)[:60]
        tts = gTTS(text=clean_text, lang='zh-tw')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        b64 = base64.b64encode(fp.getvalue()).decode()
        md = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- 3. 性感女神陣容 ---
models = {
    "🔥 台灣火辣名模": "https://images.pexels.com/photos/1382731/pexels-photo-1382731.jpeg?auto=compress&cs=tinysrgb&w=800",
    "💃 冷艷時尚女神": "https://images.pexels.com/photos/1462637/pexels-photo-1462637.jpeg?auto=compress&cs=tinysrgb&w=800",
    "💋 誘惑內衣模特": "https://images.pexels.com/photos/3005341/pexels-photo-3005341.jpeg?auto=compress&cs=tinysrgb&w=800"
}

# --- 4. 介面佈局 ---
st.markdown("<h1 style='text-align: center; color: #ff1493;'>💋 性感AI女孩：2.0 Flash 硬核戰情室 💋</h1>", unsafe_allow_html=True)

task_list = ["1. IP 偵測", "2. Top 10 排行", "3. 錯誤偵測", "4. 延遲診斷", "5. 入侵偵測", "6. 萬能百科"]

col1, col2, col3 = st.columns([1, 1.2, 1.5])

with col1:
    st.markdown("### 🛠️ 數據中心")
    uploaded_files = st.file_uploader("📂 上傳日誌", accept_multiple_files=True)
    choice = st.selectbox("值班女神：", list(models.keys()))
    st.session_state.model_url = models[choice]
    st.info("💡 提示：2.0 額度較緊，女神會自動重試喔！")

with col2:
    # 修正語法：width='stretch' 消除警告
    st.image(st.session_state.model_url, width='stretch')

with col3:
    selected_task = st.selectbox("任務指標：", task_list, index=st.session_state.task_index)
    ans_container = st.container(height=500)

# --- 5. 核心邏輯處理 (死守 2.0 + 自動重試) ---
if prompt := st.chat_input("跟女神說說話..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with col3:
        with ans_container:
            # 顯示歷史訊息
            for m in st.session_state.messages:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])
            
            with st.chat_message("assistant"):
                # 限制 log 長度以節省 Token，增加成功率
                logs = ""
                if uploaded_files:
                    for f in uploaded_files:
                        raw = f.read()
                        try: logs += raw.decode('utf-8')[:200]
                        except: logs += raw.decode('cp950', errors='ignore')[:200]
                
                # --- 硬核重試機制 ---
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        client = genai.Client(api_key=MY_KEY)
                        # 模型名稱統一使用 'gemini-2.0-flash'，避開 404
                        response = client.models.generate_content(
                            model='gemini-2.0-flash', 
                            contents=f"你是性感AIOps專家。任務：{selected_task}。數據：{logs}。指令：{prompt}。請給出專業分析並撒嬌。"
                        )
                        
                        ans_text = response.text
                        st.markdown(ans_text)
                        st.session_state.messages.append({"role": "assistant", "content": ans_text})
                        sexy_speak(ans_text)
                        break # 成功就跳出循環
                        
                    except Exception as e:
                        if "429" in str(e) and attempt < max_attempts - 1:
                            wait_time = 25 # 2.0 免費版建議等待秒數
                            st.warning(f"哥哥... 2.0 說它現在太擠了，女神幫你在門口排隊，倒數 {wait_time} 秒後自動重新敲門喔！")
                            time.sleep(wait_time)
                            st.rerun() # 重新執行以觸發下一輪嘗試
                        else:
                            st.error(f"哥哥拍拍，2.0 真的體力不支了：{e}")
                            break