from openai import OpenAI
import streamlit as st
import requests
import json
from logger import *

# 初始化 session state
if "button_clicked" not in st.session_state:
    st.session_state["button_clicked"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "请输入您的需求，我将会调用API为您解决～"}]
if "rewoo_state" not in st.session_state:
    st.session_state["rewoo_state"] = None
if "api_recommendations" not in st.session_state:
    st.session_state["api_recommendations"] = None

def check_yes():
    # 用户确认后继续执行计划
    url_continue = "http://localhost:8000/execute_plan"
    state_str = st.session_state["rewoo_state"]

    if state_str:
        response = requests.post(url_continue, json={"rewoo_state": st.session_state["rewoo_state"]})
        if response.status_code == 200:
            try:
                response_json = response.json()
                logger.info(f"Full response JSON: {response_json}")
                if "response" in response_json:
                    msg = response_json["response"]
                else:
                    logger.error("Key 'response' not found in the response JSON")
                    msg = "Unexpected response format"
            except ValueError as e:
                logger.error(f"JSON decoding failed: {e}")
                msg = "Invalid JSON response"
        else:
            msg = "继续执行时 API 调用失败"
        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.session_state["rewoo_state"] = None  # 重置状态
        st.session_state["button_clicked"] = False
        st.session_state["api_recommendations"] = None
        st.rerun()

# 侧边栏设置
with st.sidebar:
    st.sidebar.title("API 计划信息")
    if st.session_state["rewoo_state"]:
        steps = st.session_state['rewoo_state']['steps']
        for i, step in enumerate(steps):
            st.sidebar.write(f"步骤 {i + 1}: {step[0]}")
            if st.sidebar.button(f"删除步骤 {i + 1}", key=f"delete_{i}"):
                del st.session_state['rewoo_state']['steps'][i]
                st.rerun()
            if st.sidebar.button(f"修改步骤 {i + 1}", key=f"edit_{i}"):
                st.session_state['edit_step'] = i
                st.session_state['edit_content'] = step
                st.experimental_rerun()

if 'edit_step' in st.session_state:
    st.title("编辑步骤")
    step = st.session_state['edit_content']
    new_description = st.text_input("步骤描述", value=step[0])
    new_tool = st.text_input("工具", value=step[2])
    new_parameter = st.text_input("参数", value=step[3])
    if st.button("保存修改"):
        st.session_state['rewoo_state']['steps'][st.session_state['edit_step']] = (new_description, step[1], new_tool, new_parameter)
        del st.session_state['edit_step']
        del st.session_state['edit_content']
        st.rerun()

st.title("API 编排 Demo")
st.caption("🚀 通过 ReWOO 方式一次生成全部的 API 编排计划，然后依次执行")

# 显示对话记录
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 用户输入处理
if prompt := st.chat_input(placeholder="请输入您的问题..."):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 调用 /chat 端点生成计划
    url_chat = "http://localhost:8000/get_plan"
    payload = {"message": prompt}
    response = requests.post(url_chat, json=payload)

    if response.status_code == 200:
        data = response.json()
        msg = data["response"]
        print(f"msg: {data}")
        # 直接存储一个 rewoo 对象
        st.session_state["rewoo_state"] = data["rewoo_state"]
        if "api_recommendations" in data:
            st.session_state["api_recommendations"] = data["api_recommendations"]
    else:
        msg = "生成计划时 API 调用失败"

    st.session_state["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    st.rerun()

# 如果有未执行的计划，显示确认按钮
if st.session_state["rewoo_state"]:
    if st.button("确认执行计划", on_click=check_yes):
        st.session_state["button_clicked"] = True

# 检查是否点击了确认按钮
if st.session_state["button_clicked"]:
    check_yes()