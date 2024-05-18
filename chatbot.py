from openai import OpenAI
import streamlit as st
import requests
import json

# 初始化session state
if "button_clicked" not in st.session_state:
    st.session_state["button_clicked"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
if "state" not in st.session_state:
    st.session_state["state"] = None

def check_yes():
    # 用户确认后继续执行计划
    url_continue = "http://localhost:8000/continue"
    state_str = st.session_state["state"]

    if state_str:
        response = requests.post(url_continue, json={"state": state_str})
        if response.status_code == 200:
            msg = response.json()["response"]
        else:
            msg = "继续执行时API调用失败"
        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.session_state["state"] = None  # 重置状态
        st.session_state["button_clicked"] = False
        st.rerun()

# 侧边栏设置
with st.sidebar:
    qwen_api_key = st.text_input("Qwen API Key", key="qwen_api_key", type="password")
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

    """
    编排模式：
    1.Auto：直接以ReWOO的形式执行
    2.Validation：以ReWOO方式生成API编排计划，通过人工确认后再执行
    3.Manual：人工编排整个API流程
    """
    mode = st.selectbox("Mode", ["Auto", "Validation", "Manual"])

st.title("API编排Demo")
st.caption("🚀 通过ReWOO方式一次生成全部的API编排计划，然后依次执行")

# 显示对话记录
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 用户输入处理
if prompt := st.chat_input():
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 调用 /chat 端点生成计划
    url_chat = "http://localhost:8000/chat"
    payload = {"message": prompt}
    response = requests.post(url_chat, json=payload)

    if response.status_code == 200:
        data = response.json()
        msg = data["response"]
        print(f"msg:{data}")
        st.session_state["state"] = data["state"]
    else:
        msg = "生成计划时API调用失败"

    st.session_state["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

# 如果有未执行的计划，显示确认按钮
if st.session_state["state"]:
    if st.button("确认执行计划", on_click=check_yes):
        st.session_state["button_clicked"] = True

# 检查是否点击了确认按钮
if st.session_state["button_clicked"]:
    check_yes()