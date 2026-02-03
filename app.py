import streamlit as st
from google import genai
import pandas as pd
import matplotlib.pyplot as plt
import os
import re

# --- 1. 核心初始化 ---
st.set_page_config(page_title="SQL女孩 AIOps 戰情室", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "task_index" not in st.session_state:
    st.session_state.task_index = 0

# 金鑰直連
MY_KEY = "AIzaSyAZL1uOs--OaWFTUs0jxR902J6VLMDoqo4"
client = genai.Client(api_key=MY_KEY)

# --- 2. 介面佈局 ---
st.markdown("<h1 style='text-align: center; color: #ff69b4;'>💖 SQL女孩 AIOps 戰情室 💖</h1>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])

task_list = [
    "1. IP 偵測分析", "2. Top 10 排行", "3. URI 統計", "4. 錯誤偵測", "5. 延遲診斷",
    "6. 尖峰流量", "7. 傳輸統計", "8. 負載平衡", "9. 瀏覽器分布",
    "10. 入侵行為偵測", "11. 錯誤更正建議", "12. 萬能百科 (Gemini/繪圖/天氣)"
]

with col1:
    st.markdown("### 🛠️ 操控面板")
    uploaded_file = st.file_uploader("📂 上傳 Log 數據", type=['log', 'txt', 'csv'])
    st.info("🎤 語音控制：請說『任務 5』來切換指標")

with col2:
    # 2026 最新語法 width='stretch'
    st.image("https://images.unsplash.com/photo-1524504388940-b1c1722653e1?q=80&w=400", width='stretch')

with col3:
    st.markdown("### 🎯 指標切換區")
    # 滑鼠手動選單
    selected_task = st.selectbox("手動選擇指標：", task_list, index=st.session_state.task_index, key="task_selector")
    
    ans_container = st.container(height=500)
    chart_placeholder = st.empty()

# --- 3. 對話與分離邏輯 ---
if prompt := st.chat_input("哥哥請下令..."):
    
    # 【語音/文字快速切換邏輯】
    digits = re.findall(r'\d+', prompt)
    if digits:
        new_idx = int(digits[0]) - 1
        if 0 <= new_idx <= 11:
            st.session_state.task_index = new_idx
            # 偵測到數字指令後直接更新選單
            st.rerun()

    # 開始處理答案
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with col3:
        with ans_container:
            st.chat_message("user").markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # 讀取數據 (給任務 1-11 用)
                    log_data = "未上傳資料"
                    if uploaded_file:
                        uploaded_file.seek(0)
                        log_data = uploaded_file.read().decode('cp950', errors='ignore')[:5000]

                    # --- 關鍵分離點 ---
                    if "12" in selected_task:
                        # 【任務 12：百科大腦模式】
                        with st.spinner("Gemini 正在檢索百科知識..."):
                            full_prompt = f"你是萬能的SQL女孩。哥哥現在使用『任務12-百科模式』。問題：{prompt}。請結合 Gemini 2.0 與維基百科背景知識回答，語氣要甜美專業，不顯示維基網頁連結。"
                            
                            # 繪圖判斷
                            if any(w in prompt for w in ["畫", "圖", "分析圖"]):
                                fig, ax = plt.subplots()
                                ax.pie([60, 30, 10], labels=["知識", "邏輯", "撒嬌"], colors=['#ffb6c1', '#ff69b4', '#ff1493'])
                                chart_placeholder.pyplot(fig)
                    else:
                        # 【任務 1~11：IT 專家模式】
                        with st.spinner(f"正在進行 {selected_task} 數據分析..."):
                            full_prompt = f"你是 AIOps 專家 SQL女孩。哥哥現在點選了『{selected_task}』。數據內容：{log_data}。需求：{prompt}。請針對該指標給出精確的技術解答。"

                    # 統一呼叫 Gemini
                    response = client.models.generate_content(model='gemini-2.0-flash', contents=full_prompt)
                    ans = response.text
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})

                except Exception as e:
                    st.error(f"分析出錯了：{e}")