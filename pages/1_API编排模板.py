import streamlit as st
import networkx as nx
from pyvis.network import Network
import tempfile
import json


def read_cache(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def create_graph(steps):
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
    nt = Network("300px", "300px", heading="", bgcolor="white", font_color="black")
    nt.from_nx(G)
    nt.set_options(
        """
    var options = {
        "interaction": {
            "zoomView": false,
            "dragView": false
        },
        "physics": {
            "enabled": false
        }
    }
    """
    )

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
        border: 2px solid white;
        border-radius: 10px;
        overflow: hidden;
    }}
    .title {{
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        margin-top: 10px;
        color: black;
    }}
    a {{
        text-decoration: none;
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    </style>
    """
    return css + source_code


def main():
    st.title("API编排模板")

    # Read cache.json
    data = read_cache("cache.json")

    # Filter graphs to include only those with more than one node
    filtered_data = {
        key: value for key, value in data.items() if len(value.get("steps", [])) > 1
    }

    # Display graphs in rows of four
    num_cols = 4
    keys = list(filtered_data.keys())
    num_keys = len(keys)
    num_rows = (num_keys + num_cols - 1) // num_cols  # Calculate number of rows needed

    for row in range(num_rows):
        cols = st.columns(num_cols)
        for col in range(num_cols):
            idx = row * num_cols + col
            if idx < num_keys:
                key = keys[idx]
                value = filtered_data[key]
                steps = value.get("steps", [])
                graph_html = create_graph(steps)
                link_html = f"""
                <a href="https://www.google.com" target="_blank">
                    <div style="height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        {graph_html}
                        <div class="title">{key}</div>
                    </div>
                </a>
                """
                with cols[col]:
                    st.components.v1.html(
                        link_html, height=360
                    )  # Ensure container is large enough for graph and border


if __name__ == "__main__":
    main()
