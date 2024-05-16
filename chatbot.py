from openai import OpenAI
import streamlit as st

if "button_clicked" not in st.session_state:
    st.session_state["button_clicked"] = True

def check_yes():
    # 应该把编排得到的API依次调用
    # 还是得通过ReWOO来执行编排
    st.session_state.button_clicked = True

with st.sidebar:
    qwen_api_key = st.text_input("Qwen API Key", key="qwen_api_key", type="password")
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    
    """
    编排模式：
    1.Auto：直接以ReWOO的形式执行
    2.Validation：以ReWOO方式生成API编排计划，通过人工确认后再执行
    3.Manual：人工编排整个API流程
    """
    mode = st.selectbox("Mode",["Auto","Semi-Auto","Manual"])
    # mode = st.selectbox("Mode", ["ReWOO", "ReACT","LLMCompiler","Manual"])
    if not st.session_state.button_clicked:
        check_yes = st.button("执行编排流程", key="ok", on_click=check_yes, disabled=False, use_container_width=True)

st.title("蔡卓悦的API编排demo")
st.caption("🚀 通过ReWOO方式一次生成全部的API编排计划，然后依次执行")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
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
        st.session_state["button_clicked"] = False
        st.experimental_rerun()
    else:
        msg = "API调用失败"
    
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
