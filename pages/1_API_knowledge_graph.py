import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json

# 创建两列布局
left_col, right_col = st.columns([3, 1])  # 左侧占3份宽度，右侧占1份宽度

# 配置图表
config = Config(
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
with right_col:
    return_value = agraph(
        nodes=nodes,
        edges=edges,
        config=config
    )

# 在左侧列中显示其他内容
with left_col:
    st.title("Main Content")
    st.write("This is the main content area.")
    # 你可以在这里添加更多的内容和组件
