import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json

# 设置自定义CSS来更改左列的背景颜色
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
    unsafe_allow_html=True
)

# 创建两列布局

# 配置图表
config = Config(
    width=450,  # 调整宽度以适应右侧列
    height=800,
    directed=True,
    physics=True,
    nodeHighlightBehavior=True,
    highlightColor="#F7A7A6",
    collapsible=True,
    node={'labelProperty': 'label'},
    link={'labelProperty': 'label', 'renderLabel': True}
)

# 读取JSON文件
with open('marvel_graph_data.json') as f:
    data = json.load(f)

# 从JSON文件中获取节点和边
nodes = [Node(**node) for node in data['nodes']]
edges = [Edge(**edge) for edge in data['edges']]

# 在右侧列中显示图谱

return_value = agraph(
    nodes=nodes,
    edges=edges,
    config=config
)

