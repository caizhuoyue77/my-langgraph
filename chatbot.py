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
if "add_step" not in st.session_state:
    st.session_state["add_step"] = False

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

def reset_edit_state():
    st.session_state['edit_step'] = None
    st.session_state['edit_content'] = None
    st.session_state['add_step'] = False

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

# 显示和管理步骤
if st.session_state["rewoo_state"]:
    st.header("API 计划信息")
    steps = st.session_state['rewoo_state']['steps']

    for i, step in enumerate(steps):
        with st.expander(f"步骤 {i + 1}: {step[0]}", expanded=True):
            # st.write(f"当前步骤内容: {step}")
            if st.session_state["api_recommendations"]:
                tool_options = st.session_state["api_recommendations"]
            else:
                tool_options = []  # 默认工具选项，如果没有api_recommendations

            new_step_name = st.text_input("步骤名称", value=step[0], key=f"step_name_{i}")
            new_tool = st.selectbox("工具", tool_options, index=tool_options.index(step[2]) if step[2] in tool_options else 0, key=f"tool_{i}")
            new_parameter = st.text_input("参数", value=step[3], key=f"parameter_{i}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("保存修改", key=f"save_{i}"):
                    new_step = (new_step_name, step[1], new_tool, new_parameter)
                    st.session_state['rewoo_state']['steps'][i] = new_step
                    st.session_state['messages'].append({"role": "assistant", "content": "修改成功"})
                    st.experimental_rerun()
            with col2:
                if st.button("删除步骤", key=f"delete_{i}"):
                    del st.session_state['rewoo_state']['steps'][i]
                    st.experimental_rerun()

    if st.button("添加步骤"):
        st.session_state['add_step'] = True

    if st.session_state['add_step']:
        st.header("添加步骤")

        if st.session_state["api_recommendations"]:
            tool_options = st.session_state["api_recommendations"]
        else:
            tool_options = []  # 默认工具选项，如果没有api_recommendations
        
        new_step_name = st.text_input("步骤名称", key="new_step_name")
        new_tool = st.selectbox("工具", tool_options, key="new_tool")
        new_parameter = st.text_input("参数", key="new_parameter")
        insert_position = st.number_input("插入位置", min_value=1, max_value=len(steps) + 1, value=len(steps) + 1, key="insert_position")

        if st.button("保存步骤"):
            new_step = (new_step_name, "", new_tool, new_parameter)
            st.session_state['rewoo_state']['steps'].insert(insert_position - 1, new_step)
            st.session_state['messages'].append({"role": "assistant", "content": "步骤添加成功"})

            reset_edit_state()
            st.experimental_rerun()
        
        if st.button("取消"):
            reset_edit_state()

# 如果有未执行的计划，显示确认按钮
if st.session_state["rewoo_state"]:
    if st.button("确认执行计划", on_click=check_yes):
        st.session_state["button_clicked"] = True

# 检查是否点击了确认按钮
if st.session_state["button_clicked"]:
    check_yes()