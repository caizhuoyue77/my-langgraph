import streamlit as st
import random
import networkx as nx
from pyvis.network import Network
import tempfile


def create_graph(color):
    # 创建图
    G = nx.Graph()
    nodes = ["Node 1", "Node 2", "Node 3"]
    edges = [("Node 1", "Node 2"), ("Node 2", "Node 3"), ("Node 3", "Node 1")]

    for node in nodes:
        G.add_node(node)

    for edge in edges:
        G.add_edge(*edge)

    # 生成网络图
    nt = Network("300px", "300px", heading="", bgcolor=color, font_color="white")
    nt.from_nx(G)
    nt.show_buttons(filter_=["physics"])

    # 使用临时文件来存储并读取HTML
    with tempfile.NamedTemporaryFile(delete=True, suffix=".html") as tmpfile:
        nt.save_graph(tmpfile.name)
        with open(tmpfile.name, "r", encoding="utf-8") as HtmlFile:
            source_code = HtmlFile.read()

    # 将CSS直接嵌入HTML以确保样式生效
    css = f"""
    <style>
    .network {{
        width: 100%;
        height: 100%;
        border: none;
        border-radius: 10px;
        overflow: hidden;
    }}
    </style>
    """
    return css + source_code


def main():
    st.title("带链接的动态莫兰蒂色系彩色方框含知识图谱")

    colors = {
        "soft-pink": "#efc1d3",
        "soft-green": "#a8bece",
        "soft-purple": "#a7a5c6",
        "soft-yellow": "#decba5",
        "soft-grey": "#cccccc",
        "soft-blue": "#b1bcc8",
        "soft-orange": "#f2d3ab",
        "soft-teal": "#accddc",
    }

    # 动态创建带链接的方框
    for _ in range(2):  # 仅创建两行方框以避免重复生成太多图谱
        cols = st.columns(4)
        for idx in range(4):
            with cols[idx]:
                color = random.choice(list(colors.values()))
                graph_html = create_graph(color)
                link_html = f"""
                <a href="https://www.google.com" target="_blank" style="text-decoration: none;">
                    <div style="height: 300px;">
                        {graph_html}
                    </div>
                </a>
                """
                st.components.v1.html(
                    link_html, height=330
                )  # 确保容器足够容纳图谱和边框


if __name__ == "__main__":
    main()
