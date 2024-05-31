import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json

# 配置图表
config = Config(
    width=300,  # 调整宽度
    height=800, 
    directed=True,
    physics=True,
    nodeHighlightBehavior=True, 
    highlightColor="#F7A7A6",
    collapsible=True,
    node={'labelProperty': 'label', 'size': 10},  # 调整节点大小
    link={'labelProperty': 'label', 'renderLabel': True}
)

# 读取JSON文件
with open('marvel_graph_data.json') as f:
    data = json.load(f)

# 从JSON文件中获取节点和边，并调整节点大小
nodes = [Node(**node) for node in data['nodes']]  # 在此处调整节点大小
edges = [Edge(**edge) for edge in data['edges']]

# 在侧边栏中显示图谱
with st.sidebar:
    return_value = agraph(
        nodes=nodes,
        edges=edges,
        config=config
    )

# 在主内容区域显示其他内容
st.title("Main Content")
st.write("This is the main content area.")
# 你可以在这里添加更多的内容和组件
