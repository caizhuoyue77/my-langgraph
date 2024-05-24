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
if "edit_step" not in st.session_state:
    st.session_state["edit_step"] = None
if "edit_content" not in st.session_state:
    st.session_state["edit_content"] = None

def check_yes():
    # 用户确认后继续执行计划
    url_continue = "http://localhost:8000/execute_plan"

    state_str = st.session_state["rewoo_state"]

    if state_str:
        response = requests.post(url_continue, json={"rewoo_state": state_str})
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
        st.experimental_rerun()

# 侧边栏设置
with st.sidebar:
    st.sidebar.title("API 计划信息")
    if st.session_state["rewoo_state"]:
        steps = st.session_state['rewoo_state']['steps']
        for i, step in enumerate(steps):
            st.sidebar.write(f"步骤 {i + 1}: {step[0]}")
            if st.sidebar.button(f"删除步骤 {i + 1}", key=f"delete_{i}"):
                del st.session_state['rewoo_state']['steps'][i]
                st.experimental_rerun()
            if st.sidebar.button(f"修改步骤 {i + 1}", key=f"edit_{i}"):
                st.session_state['edit_step'] = i
                st.session_state['edit_content'] = step
                st.experimental_rerun()

    # 固定位置的编辑/修改区域
    if st.session_state['edit_step'] is not None:
        st.sidebar.title("编辑步骤")

        step = st.session_state['edit_content']
        if st.session_state["api_recommendations"]:
            tool_options = st.session_state["api_recommendations"]
        else:
            tool_options = []  # 默认工具选项，如果没有api_recommendations
        
        if step[2] in tool_options:
            selected_index = tool_options.index(step[2])
        else:
            selected_index = 0  # 如果工具不在选项中，选择第一个选项作为默认值

        new_tool = st.sidebar.selectbox("工具", tool_options, index=selected_index)
        new_parameter = st.sidebar.text_input("参数", value=step[3])
        
        if st.sidebar.button("保存修改"):
            # 更新选中的步骤
            # st.session_state['rewoo_state']['steps'][st.session_state['edit_step']] = (step[0], step[1], new_tool, new_parameter)

            st.session_state['rewoo_state']['steps'] = [ st.session_state['rewoo_state']['steps'][0] ]
            
            st.session_state['messages'].append({"role": "assistant", "content": "修改成功"})

            # 清除编辑状态
            st.session_state['edit_step'] = None
            st.session_state['edit_content'] = None
            
            # 重新运行脚本
            st.experimental_rerun()
        
        if st.sidebar.button("取消修改"):
            # 清除编辑状态
            st.session_state['edit_step'] = None
            st.session_state['edit_content'] = None

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
        # 直接存储一个新的 rewoo 对象
        st.session_state["rewoo_state"] = data["rewoo_state"]
        if "api_recommendations" in data:
            st.session_state["api_recommendations"] = data["api_recommendations"]
    else:
        msg = "生成计划时 API 调用失败"

    st.session_state["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
    st.experimental_rerun()

# 如果有未执行的计划，显示确认按钮
if st.session_state["rewoo_state"]:
    if st.button("确认执行计划", on_click=check_yes):
        st.session_state["button_clicked"] = True

# 检查是否点击了确认按钮
if st.session_state["button_clicked"]:
    check_yes()
