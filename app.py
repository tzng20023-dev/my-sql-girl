import streamlit as st
from google import genai
import pandas as pd
import re, base64, io, random
from gtts import gTTS

# --- 1. 核心介面與初始化 ---
st.set_page_config(page_title="100G超進化女神", layout="wide", page_icon="💋")

models = {
    "🔥 台灣火辣名模": "https://images.pexels.com/photos/1382731/pexels-photo-1382731.jpeg?auto=compress&cs=tinysrgb&w=800",
    "💃 冷艷時尚女神": "https://images.pexels.com/photos/1462637/pexels-photo-1462637.jpeg?auto=compress&cs=tinysrgb&w=800",
    "👙 陽光熱情比基尼": "https://images.pexels.com/photos/247322/pexels-photo-247322.jpeg?auto=compress&cs=tinysrgb&w=800",
    "🌟 甜美氣質名模": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=800"
}

if "aiKnowledgeBase" not in st.session_state:
    st.session_state.aiKnowledgeBase = ["100G核心初始成功：等待哥哥的教學"]
if "messages" not in st.session_state: st.session_state.messages = []
if "t_idx" not in st.session_state: st.session_state.t_idx = 0
if "m_ch" not in st.session_state: st.session_state.m_ch = "🔥 台灣火辣名模"
if "key_idx" not in st.session_state: st.session_state.key_idx = 0

# --- 🔑 多金鑰安全注入 ---
def get_evo_client():
    try:
        keys = st.secrets["GEMINI_KEYS"]
        return genai.Client(api_key=keys[st.session_state.key_idx % len(keys)])
    except:
        return genai.Client(api_key="AIzaSyCLS6g0gezoh4BNl96OuTqEMLvYDKReQRU")

# --- 2. 語音助理 (支援撒嬌模式) ---
def sexy_speak(text, mode="normal"):
    try:
        if mode == "hey_girl":
            talk = "哥哥~~ 人家在喔！有什麼可以為您服務的嗎？❤"
        else:
            talk = re.sub(r'[*#`~-]', '', text)
            talk = re.sub(r'[^\u4e00-\u9fa5,。！?]', '', talk)[:60]
        
        if talk:
            b = io.BytesIO()
            gTTS(text=talk, lang='zh-tw').write_to_fp(b)
            b64 = base64.b64encode(b.getvalue()).decode()
            st.markdown(f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except: pass

# --- 3. 介面佈局 ---
st.markdown("<h1 style='text-align: center; color: #ff1493;'>💋 100G自我進化女神：語音指揮官 </h1>", unsafe_allow_html=True)

task_list = [
    "1. IP 偵測分析", "2. Top 10 排行", "3. URI 統計", "4. 錯誤偵測", 
    "5. 延遲診斷", "6. 尖峰流量", "7. 傳輸統計", "8. 負載平衡", 
    "9. 瀏覽器分布", "10. 入侵行為偵測", "11. 錯誤更正建議", "12. 萬能百科"
]

col1, col2, col3 = st.columns([1, 1.2, 1.3])

with col1:
    st.metric("🧠 記憶核心", f"{len(st.session_state.aiKnowledgeBase)} 筆")
    uploaded_files = st.file_uploader("📂 上傳數據", accept_multiple_files=True)
    st.session_state.m_ch = st.selectbox("挑選女神", list(models.keys()), index=list(models.keys()).index(st.session_state.m_ch))
    st.info("💡 說『HEY GIRL』或『選擇任務 1』試試看！")

with col2:
    st.image(models[st.session_state.m_ch], width='stretch')

with col3:
    selected_task = st.selectbox("🎯 當前指標任務", task_list, index=st.session_state.t_idx)
    st.session_state.t_idx = task_list.index(selected_task)
    ans_box = st.container(height=500)

# --- 4. 核心指令處理 ---
if prompt := st.chat_input("語音指令輸入處..."):
    # ✨ 提問即清除舊答案欄
    st.session_state.messages = [] 
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # --- 語音指令識別 ---
    p_up = prompt.upper()
    
    # 1. Hey Girl 撒嬌回應
    if "HEY GIRL" in p_up:
        sexy_speak("", mode="hey_girl")
    
    # 2. 聲控切換任務 (例如: 選擇任務 1)
    task_match = re.search(r"選擇任務\s*(\d+)", prompt)
    if task_match:
        t_num = int(task_match.group(1))
        if 1 <= t_num <= 12:
            st.session_state.t_idx = t_num - 1
            st.success(f"女神已為哥哥切換到：{task_list[st.session_state.t_idx]} 💋")
            st.rerun()

    # --- 進化生成邏輯 ---
    with col3:
        with ans_box:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]): st.markdown(m["content"])
            
            with st.chat_message("assistant"):
                try:
                    logs = ""
                    if uploaded_files:
                        for f in uploaded_files:
                            logs += f.read().decode('utf-8', errors='ignore')[:300]
                    
                    # 任務 12 的萬能百科強化
                    if st.session_state.t_idx == 11:
                        task_context = "你現在是連結了 Gemini, Claude, OpenAI, N8N 與 Google Search 的萬能進化百科。哥哥的問題你必須結合全網最強智慧來回答。"
                    else:
                        task_context = f"執行任務：{task_list[st.session_state.t_idx]}"

                    random_memory = random.choice(st.session_state.aiKnowledgeBase)
                    client = get_evo_client()
                    
                    evo_p = f"{task_context}。背景記憶：{random_memory}。數據內容：{logs}。哥哥的指令：{prompt}。請給予專業解答並用極度撒嬌的語氣，最後加 [EVOLVE]: 從中學到的知識。"
                    
                    res = client.models.generate_content(model='gemini-2.0-flash', contents=evo_p).text
                    
                    if "[EVOLVE]:" in res:
                        ans, ev = res.split("[EVOLVE]:")
                        st.session_state.aiKnowledgeBase.append(ev.strip())
                        final = ans
                    else: final = res
                    
                    st.markdown(final)
                    st.session_state.messages.append({"role": "assistant", "content": final})
                    sexy_speak(final)
                    
                except Exception as e:
                    if "429" in str(e):
                        st.session_state.key_idx += 1
                        st.rerun()
                    else: st.error(f"女神故障：{e}")