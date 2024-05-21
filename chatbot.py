from openai import OpenAI
import streamlit as st
import requests
import json
from logger import *

# 初始化 session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "memory" not in st.session_state:
    st.session_state["memory"] = {}

# 侧边栏设置
with st.sidebar:
    st.sidebar.title("记忆信息")
    if st.session_state["memory"]:
        st.sidebar.json(st.session_state["memory"])
    else:
        st.sidebar.write("暂无计划信息")

st.title("长记忆Demo")
st.caption("🚀 每x轮对话归纳总结记忆")

# 显示对话记录
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 用户输入处理
if prompt := st.chat_input(placeholder="请输入您的问题..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 调用 /chat 端点生成计划
    url_chat = "http://localhost:8000/chat_with_memory"
    payload = {"message": prompt}
    response = requests.post(url_chat, json=payload)

    if response.status_code == 200:
        data = response.json()
        msg = data["response"]
        # 直接存储一个 memory_main 对象
        if "memory" in data:
            st.session_state["memory"] = data["memory"]
    else:
        msg = "生成计划时 API 调用失败"

    

    # st.session_state["messages"].append({"role": "assistant", "content": msg})
    # st.chat_message("assistant").write(msg)

    messages = st.session_state["messages"]

    # logger.critical(len(messages))

    if(len(messages) % 5 ==0 ): # 每6轮对话抽取一次记忆内容
    #     # 去存储记忆
        logger.critical("存储记忆")
        
        url_chat = "http://localhost:8010/store-memory/"

        payload = {"messages": str(messages[-6:]), "user_name": "用户", "bot_name": "Default Bot"}
        response = requests.post(url_chat, json=payload)
        if response.status_code == 200:
            data = response.json()
            new_msg = data["response"]
            logger.error(new_msg)
        else:
            new_msg = "存储记忆时 API 调用失败"

        msg += new_msg

    msg += str(len(messages))

    st.session_state["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

    st.rerun()




