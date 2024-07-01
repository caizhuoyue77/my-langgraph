import streamlit as st
import random
import networkx as nx
from pyvis.network import Network
import tempfile
import json


def read_cache(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def create_graph(color, title, steps):
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes for each step
    for idx, step in enumerate(steps):
        node_label = step[2]  # Use the third value in the step as node label
        G.add_node(node_label)

    # Add edges between steps
    for i in range(len(steps) - 1):
        source_label = steps[i][2]  # Node label from current step
        target_label = steps[i + 1][2]  # Node label from next step
        G.add_edge(source_label, target_label)

    # Generate network graph
    nt = Network("300px", "300px", heading="", bgcolor=color, font_color="white")
    nt.from_nx(G)
    nt.show_buttons(filter_=["physics"])

    # Use a temporary file to store and read HTML
    with tempfile.NamedTemporaryFile(delete=True, suffix=".html") as tmpfile:
        nt.save_graph(tmpfile.name)
        with open(tmpfile.name, "r", encoding="utf-8") as HtmlFile:
            source_code = HtmlFile.read()

    # Embed CSS directly into HTML to ensure styles are applied
    css = f"""
    <style>
    .network {{
        width: 100%;
        height: 100%;
        border: none;
        border-radius: 10px;
        overflow: hidden;
    }}
    .title {{
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        margin-top: 10px;
    }}
    </style>
    """
    # Add title to the bottom of the graph
    title_html = f'<div class="title">{title}</div>'

    return css + source_code + title_html


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

    # Read cache.json
    data = read_cache("cache.json")

    # Dynamically create colored boxes with links
    for key, value in data.items():
        steps = value.get("steps", [])
        # Skip tasks with only one step
        if len(steps) < 2:
            continue

        cols = st.columns(4)
        for idx in range(4):
            with cols[idx]:
                color = random.choice(list(colors.values()))
                graph_html = create_graph(color, key, steps)
                link_html = f"""
                <a href="https://www.google.com" target="_blank" style="text-decoration: none;">
                    <div style="height: 300px;">
                        {graph_html}
                    </div>
                </a>
                """
                st.components.v1.html(
                    link_html, height=360
                )  # Ensure container is large enough for graph and border


if __name__ == "__main__":
    main()
