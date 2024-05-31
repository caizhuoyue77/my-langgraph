import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config, ConfigBuilder
import json

config_builder = ConfigBuilder()
config = config_builder.build()

config = Config(width=200, 
                height=400, 
                directed=True,
                physics=True,
                nodeHighlightBehavior=True, 
                highlightColor="#F7A7A6",
                collapsible=True,
                node={'labelProperty':'label'},
                link={'labelProperty': 'label', 'renderLabel': True}
                ) 

# 读取JSON文件
with open('marvel_graph_data.json') as f:
    data = json.load(f)

# 从JSON文件中获取节点和边
nodes = [Node(**node) for node in data['nodes']]
edges = [Edge(**edge) for edge in data['edges']]

# 配置
config = Config(
    width=750,
    height=950,
    directed=True,
    physics=True,
    hierarchical=False,
)

# 创建图形
return_value = agraph(
    nodes=nodes,
    edges=edges,
    config=config
)