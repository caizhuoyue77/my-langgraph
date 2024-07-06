import streamlit as st
import requests
import json
import networkx as nx
from pyvis.network import Network
import tempfile

API_URL = "http://localhost:8000/delete"  # 后端 API 的 URL


def read_cache(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def create_graph(steps):
    G = nx.DiGraph()
    for idx, step in enumerate(steps):
        node_label = step[2]
        G.add_node(node_label)
    for i in range(len(steps) - 1):
        source_label = steps[i][2]
        target_label = steps[i + 1][2]
        G.add_edge(source_label, target_label)
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
    with tempfile.NamedTemporaryFile(delete=True, suffix=".html") as tmpfile:
        nt.save_graph(tmpfile.name)
        with open(tmpfile.name, "r", encoding="utf-8") as HtmlFile:
            source_code = HtmlFile.read()
    css = """
    <style>
    .network {
        width: 100%;
        height: 100%;
        border: 2px solid white;
        border-radius: 10px;
        overflow: hidden;
        position: relative;
    }
    .title {
        text-align: center;
        font-size: 16px;
        font-weight: bold;
        margin-top: 10px;
        color: black;
    }
    a {
        text-decoration: none;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    </style>
    """
    return css + source_code


def delete_graph(key):
    response = requests.post(API_URL, json={"title": key})
    if response.status_code == 200:
        st.success(f"图表 '{key}' 删除成功")
        st.experimental_rerun()
    else:
        st.error(f"图表 '{key}' 删除失败")


def main():
    st.title("API编排模板")
    data = read_cache("cache.json")
    filtered_data = {
        key: value for key, value in data.items() if len(value.get("steps", [])) > 1
    }
    num_cols = 4
    keys = list(filtered_data.keys())
    num_keys = len(keys)
    num_rows = (num_keys + num_cols - 1) // num_cols

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
                <a href="http://localhost:8501/?title={key}" target="_blank">
                    <div style="height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        {graph_html}
                        <div class="title">{key}</div>
                    </div>
                </a>
                """
                with cols[col]:
                    st.components.v1.html(link_html, height=360)
                    if st.button(f"删除 {key}", key=f"delete_{key}"):
                        delete_graph(key)


if __name__ == "__main__":
    main()
