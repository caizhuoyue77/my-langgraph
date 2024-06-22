import streamlit as st
import requests
import logging
from streamlit_agraph import agraph, Node, Edge, Config

# 初始化日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 设置页面配置
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# 初始化 session state
default_values = {
    "button_clicked": False,
    "messages": [
        {"role": "assistant", "content": "请输入您的需求，我将会调用API为您解决～"}
    ],
    "rewoo_state": None,
    "api_recommendations": None,
    "edit_step": None,
    "edit_content": None,
    "add_step": False,
    "nodes": [],
    "edges": [],
    "show_graph": True,
    "node_size": 10,
}
for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value


def check_yes():
    """用户确认后继续执行计划"""
    url_continue = "http://localhost:8000/execute_plan"
    state_str = st.session_state["rewoo_state"]

    if state_str:
        try:
            response = requests.post(url_continue, json={"rewoo_state": state_str})
            response.raise_for_status()  # 如果状态码不是200，抛出HTTPError异常
            response_json = response.json()
            logger.info(f"Full response JSON: {response_json}")
            msg = response_json.get("response", "Unexpected response format")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            msg = "继续执行时 API 调用失败"
        except ValueError as e:
            logger.error(f"JSON decoding failed: {e}")
            msg = "Invalid JSON response"

        st.session_state["messages"].append({"role": "assistant", "content": msg})
        st.session_state["rewoo_state"] = None
        st.session_state["button_clicked"] = False
        st.session_state["api_recommendations"] = None
        st.experimental_rerun()


def reset_edit_state():
    """重置编辑状态"""
    st.session_state["edit_step"] = None
    st.session_state["edit_content"] = None
    st.session_state["add_step"] = False


def update_graph():
    """更新图节点和边"""
    # return

    data = st.session_state.get("api_recommendations", [])
    if data:
        node_size = st.session_state["node_size"]
        st.session_state["nodes"] = [
            Node(**node, size=node_size) for node in data["nodes"]
        ]
        # 根本就没有返回edge的信息似乎 我难过了

        print("This is 你要的 data 啊！")

        print(data)

        st.session_state["edges"] = [Edge(**edge) for edge in data["edges"]]


# 处理用户输入
prompt = st.chat_input(placeholder="请输入您的问题...")

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 调用 /chat 端点生成计划
    url_chat = "http://localhost:8000/get_plan"
    payload = {"message": prompt}
    try:
        response = requests.post(url_chat, json=payload)
        response.raise_for_status()  # 如果状态码不是200，抛出HTTPError异常
        data = response.json()
        msg = data["response"]
        logger.info(f"msg: {data}")
        st.session_state["rewoo_state"] = data["rewoo_state"]
        st.session_state["api_recommendations"] = data["rewoo_state"].get(
            "api_recommendations", []
        )
        logger.critical(
            f"这就是你要看的api_recommendations：{st.session_state['api_recommendations']}"
        )

        update_graph()  # 更新图数据
        st.experimental_rerun()  # 强制页面刷新

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        msg = "生成计划时 API 调用失败"

    st.session_state["messages"].append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)

# 侧边栏设置
st.sidebar.header("图谱设置")
st.session_state["show_graph"] = st.sidebar.checkbox("显示API图谱", value=True)
st.session_state["node_size"] = st.sidebar.slider(
    "API节点大小", min_value=5, max_value=50, value=10
)

# 创建列布局
col = st.columns((7, 3), gap="small")

with col[0]:
    st.title("API 编排 Demo")
    st.caption("🚀 通过 ReWOO 方式一次生成全部的 API 编排计划，然后依次执行")

    # 显示对话记录
    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

    # 显示和管理步骤
    if st.session_state["rewoo_state"]:
        st.header("API 计划信息")
        st.write("【改写后的任务】" + st.session_state["rewoo_state"]["task"])
        steps = st.session_state["rewoo_state"]["steps"]

        for i, step in enumerate(steps):
            with st.expander(f"步骤 {i + 1}: {step[0]}", expanded=True):
                tool_options = [
                    tool["name"]
                    for tool in st.session_state.get("api_recommendations", [])["nodes"]
                ]

                new_step_name = st.text_input(
                    "步骤名称", value=step[0], key=f"step_name_{i}"
                )
                new_tool = st.selectbox(
                    "工具",
                    tool_options,
                    index=tool_options.index(step[2]) if step[2] in tool_options else 0,
                    key=f"tool_{i}",
                )
                new_parameter = st.text_input(
                    "参数", value=step[3], key=f"parameter_{i}"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("保存修改", key=f"save_{i}"):
                        new_step = (new_step_name, step[1], new_tool, new_parameter)
                        st.session_state["rewoo_state"]["steps"][i] = new_step
                        st.session_state["messages"].append(
                            {"role": "assistant", "content": "修改成功"}
                        )
                        st.experimental_rerun()
                with col2:
                    if st.button("删除步骤", key=f"delete_{i}"):
                        del st.session_state["rewoo_state"]["steps"][i]
                        st.experimental_rerun()

        if st.button("添加步骤"):
            st.session_state["add_step"] = True

        if st.session_state["add_step"]:
            st.header("添加步骤")

            tool_options = st.session_state.get("api_recommendations", [])

            new_step_name = st.text_input("步骤名称", key="new_step_name")
            new_tool = st.selectbox("工具", tool_options, key="new_tool")
            new_parameter = st.text_input("参数", key="new_parameter")
            insert_position = st.number_input(
                "插入位置",
                min_value=1,
                max_value=len(steps) + 1,
                value=len(steps) + 1,
                key="insert_position",
            )

            if st.button("保存步骤"):
                new_step = (new_step_name, "", new_tool, new_parameter)
                st.session_state["rewoo_state"]["steps"].insert(
                    insert_position - 1, new_step
                )
                st.session_state["messages"].append(
                    {"role": "assistant", "content": "步骤添加成功"}
                )

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

with col[1]:
    # 自定义CSS来更改左列的背景颜色
    st.markdown(
        """
        <style>
        .left-col {
            background-color: pink;
            padding: 20px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state["show_graph"]:
        # 配置图表
        config = Config(
            width=450,
            height=800,
            directed=True,
            physics=True,
            nodeHighlightBehavior=True,
            highlightColor="#F7A7A6",
            collapsible=True,
            node={"labelProperty": "label"},
            link={"labelProperty": "label", "renderLabel": True},
        )

        nodes = st.session_state.get("nodes", [])
        edges = st.session_state.get("edges", [])

        logger.info(f"Nodes: {nodes}")
        logger.info(f"Edges: {edges}")

        if nodes:
            # 在右侧列中显示图谱
            return_value = agraph(nodes=nodes, edges=edges, config=config)
