import streamlit as st
from google import genai
import edge_tts
import asyncio
import base64
import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# --- 1. 核心設定 ---
st.set_page_config(page_title="SQL女孩 AIOps 終極任務版", layout="wide")
client = genai.Client(api_key='AIzaSyALkBgNtgFO7hHep4RLooHepuIa77JwUAo')

# --- 2. 語音輸出函數 ---
def speak(text):
    async def amain():
        fn = f"v_{int(time.time())}.mp3"
        comm = edge_tts.Communicate(text, "zh-TW-HsiaoChenNeural", rate="+15%", pitch="+5Hz")
        await comm.save(fn)
        return fn
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        fn = loop.run_until_complete(amain())
        with open(fn, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<audio autoplay><source src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
        os.remove(fn)
    except: pass

# --- 3. 視覺與背景樣式 ---
st.markdown("""
    <style>
    .stApp { background: #fdf2f4; }
    .heart-mask { 
        width: 150px; height: 130px; margin: auto; 
        clip-path: path('M75 22.5 C 75 22.5 60 0 30 0 C 10 0 0 22.5 0 52.5 C 0 90 75 150 75 150 C 75 150 150 90 150 52.5 C 150 22.5 135 0 120 0 C 90 0 75 22.5 75 22.5'); 
        background-image: url("https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=1000"); 
        background-size: cover; border: 3px solid #ff69b4; 
    }
    h2 { text-align: center; color: #ff69b4; }
    .report-box { background: white; padding: 20px; border-radius: 15px; border-left: 10px solid #ff69b4; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    </style>
    <div class="heart-mask"></div>
    <h2>💖 SQL女孩：AIOps 終極任務分析 💖</h2>
    """, unsafe_allow_html=True)

# --- 4. 自動重試機制 ---
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_ai_response(prompt):
    return client.models.generate_content(model='gemini-2.0-flash', contents=prompt)

# --- 5. 側邊欄：哥哥要求的專業任務清單 ---
st.sidebar.markdown("### 📊 AIOps 任務模式")
uploaded_file = st.sidebar.file_uploader("選取 Log (IIS/W3C 格式最佳)", type=['log', 'txt'])

task_options = [
    "A 找出 IP 連線(c-ip)與使用者(cs-username)",
    "B IP 連線排行與 Top 10 使用者分析",
    "C 最常被使用的 URI 統計",
    "E 最常出現錯誤的 URI 分析 (Error Log)",
    "F 回應時間最久分析與原因診斷",
    "G 每日小時區間尖峰使用量統計",
    "H 每日/每小時平均流量與傳輸極值",
    "I 各別主機負載平衡狀況分析",
    "J 使用者瀏覽器 (User-Agent) 類型分布",
    "K 入侵與攻擊行為現象偵測",
    "L 其他錯誤更正",
    "💕 陪我聊天"
]
selected_task = st.sidebar.selectbox("請選取分析任務:", task_options)

if st.sidebar.button("✨ 啟動分析引擎"):
    speak(f"哥哥，SQL 女孩已準備好執行任務 {selected_task[:1]}，請下達指令。")

if "messages" not in st.session_state: st.session_state.messages = []
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- 6. 核心分析與解答模板 ---
if user_input := st.chat_input("請輸入詳細指令（例如：分析前 10 名 IP）..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner(f"正在深度分析任務：{selected_task}..."):
            log_sample = ""
            if uploaded_file:
                # 讀取較多樣本以利統計分析
                log_sample = uploaded_file.read(20000).decode('cp950', errors='ignore')
                uploaded_file.seek(0)

            # 強化版 Prompt：針對具體欄位進行分析
            prompt = f"""
            你是性感專業的 AIOps 專家「SQL女孩」。
            
            【執行模式】：{selected_task}
            【分析需求】：針對哥哥的問題「{user_input}」，請分析 Log 中的 c-ip, cs-username, cs-uri-stem, sc-status, time-taken 等欄位。
            【Log 片段】：{log_sample}

            請使用以下「任務解答模板」回答：

            ---
            【💋 專家悄悄話】
            (撒嬌回應)

            【📊 任務分析解答】
            (針對該模式 {selected_task} 提供明確的統計答案與分析結果。如果是模式 B、C、E，請列出清單。)

            【💻 建議 SQL 指令/語法】
            (提供用於處理或查詢此類問題的 SQL、PowerShell 或 Python 代碼)

            【🎀 運運建議與修正】
            (針對分析結果，提供具體的優化或錯誤更正建議)
            ---
            """
            
            try:
                response = get_ai_response(prompt)
                ans = response.text
                st.markdown(f'<div class="report-box">{ans}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                
                # 語音唸出關鍵解答
                voice_part = ans.split("【📊")[1].split("\n")[1] if "【📊" in ans else "分析完成"
                speak(f"哥哥，{selected_task[:1]} 任務分析完畢。解答是：{voice_part[:100]}")
            except:
                st.error("哥哥... 資源有點擁擠，請等 30 秒後再點一次啟動喔！")