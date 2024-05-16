from openai import OpenAI
import streamlit as st


def check_yes():
    st.session_state.messages.append({"role": "assistant", "content": "点击按钮"})

with st.sidebar:
    qwen_api_key = st.text_input("Qwen API Key", key="qwen_api_key", type="password")
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    mode = st.selectbox("Mode", ["ReWOO", "ReACT","LLMCompiler","Manual"])
    check_yes = st.button("执行编排流程", on_click=check_yes, disabled=True, use_container_width=True)


st.title("蔡卓悦的API编排demo")
st.caption("🚀 通过ReWOO方式一次生成全部的API编排计划，然后依次执行")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # 原本是和OpenAI的API交互，现在改成和本地的API交互
    # client = OpenAI(api_key=openai_api_key)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    url = "http://localhost:8000/chat"

    payload = {
        "message": prompt
    }

    import requests

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        msg = response.json()["response"]
    else:
        msg = "API调用失败"
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
