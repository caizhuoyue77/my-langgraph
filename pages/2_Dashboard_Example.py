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


def create_graph(color, steps):
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
    .subtitle {{
        text-align: center;
        margin-top: 5px;
        font-size: 14px;
        color: #666666;
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

    # Read cache.json
    data = read_cache("cache.json")

    # Display graphs in rows of four
    num_cols = 4
    keys = list(data.keys())
    num_keys = len(keys)
    num_rows = num_keys // num_cols

    for row in range(num_rows):
        cols = st.columns(num_cols)
        for col in range(num_cols):
            key = keys[row * num_cols + col]
            value = data[key]
            steps = value.get("steps", [])
            color = random.choice(list(colors.values()))
            graph_html = create_graph(color, steps)
            link_html = f"""
            <a href="https://www.google.com" target="_blank" style="text-decoration: none;">
                <div style="height: 300px;">
                    {graph_html}
                    <div class="title">{key}</div>
                    <div class="subtitle">{key}</div>
                </div>
            </a>
            """
            with cols[col]:
                st.components.v1.html(
                    link_html, height=360
                )  # Ensure container is large enough for graph and border

    # If there are remaining keys that don't fill a complete row
    remaining_keys = num_keys % num_cols
    if remaining_keys > 0:
        cols = st.columns(remaining_keys)
        start_idx = num_rows * num_cols
        for idx in range(remaining_keys):
            key = keys[start_idx + idx]
            value = data[key]
            steps = value.get("steps", [])
            color = random.choice(list(colors.values()))
            graph_html = create_graph(color, steps)
            link_html = f"""
            <a href="https://www.google.com" target="_blank" style="text-decoration: none;">
                <div style="height: 300px;">
                    {graph_html}
                    <div class="title">{key}</div>
                    <div class="subtitle">{key}</div>
                </div>
            </a>
            """
            with cols[idx]:
                st.components.v1.html(
                    link_html, height=360
                )  # Ensure container is large enough for graph and border


if __name__ == "__main__":
    main()
