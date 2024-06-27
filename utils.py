import json
from functools import lru_cache


@lru_cache
def load_tools_from_file(file_path="tools_shengqian.json"):
    """从json文件中加载工具数据为json"""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_all_edges():
    """获取所有边节点"""
    return load_tools_from_file()["edges"]


def get_sementic_nodes():
    """获取语义节点"""
    return load_tools_from_file()["sementic_nodes"]


def get_tool_list_str(file_path="tools_shengqian.json"):
    """从json文件中获取工具数据为str"""
    tools_data = load_tools_from_file(file_path)["tools"]
    return get_tool_list_str_from_json_list(tools_data)


def get_tool_list_str_from_json_list(tools_data):
    """读取一个json list 转为字符串"""
    print("TOOL list")
    print(tools_data)
    return "\n".join(
        f"({i+1}) {tool['name']}[{tool['input']}]: {tool['description']}"
        for i, tool in enumerate(tools_data)
    )


def get_tools_by_type(tool_type, file_path="tools_shengqian.json"):
    """根据工具类型获取工具"""
    tools = load_tools_from_file(file_path)["tools"]
    return [tool for tool in tools if tool["type"] == tool_type]


def get_tools_by_types(tool_types, file_path="tools_shengqian.json"):
    """根据多个工具类型获取工具及其相关边"""
    tools_list = [
        tool
        for tool_type in tool_types
        for tool in get_tools_by_type(tool_type, file_path)
    ]
    related_edges = get_related_edges(
        tools_list, load_tools_from_file(file_path)["edges"]
    )
    return {"tools": tools_list, "edges": related_edges}


def get_related_edges(tools_list, edges):
    """获取相关的边"""
    tool_ids = {tool["id"] for tool in tools_list}
    return [
        edge
        for edge in edges
        if edge["source"] in tool_ids or edge["target"] in tool_ids
    ]


def get_related_nodes(tools_list, sementic_nodes, edges):
    """获取和tools有关的节点列表"""
    tool_ids = {tool["id"] for tool in tools_list}
    sementic_ids = []
    for edge in edges:
        if edge["source"] in tool_ids and edge["target"] not in tool_ids:
            sementic_ids.append(edge["target"])
        elif edge["target"] in tool_ids and edge["source"] not in tool_ids:
            sementic_ids.append(edge["source"])
    print(f"sementic_ids:{sementic_ids}")
    print([node for node in sementic_nodes if node["id"] in sementic_ids])
    return [node for node in sementic_nodes if node["id"] in sementic_ids]


if __name__ == "__main__":
    print(get_sementic_nodes())
