import json

def get_tool_list_str():
    with open("tools.json", "r") as f:
        tool_list = json.load(f)
        tool_list_str = "\n".join([
            f"({i+1}) {tool['name']}[{tool['input']}]: {tool['description']}"
            for i, tool in enumerate(tool_list["tools"])
        ])
        return tool_list_str
    
def load_tools_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        tools_data = json.load(file)
    return tools_data

def get_tools_by_types(tool_types:list):
    print(tool_types)
    tools_list = []
    for type in tool_types:
        tools = get_tools_by_type(type)
        print(tools)
        tools_list.extend(tools)
    print(tools_list)
    return tools_list

# 提取所有 type 为某个值的工具
def get_tools_by_type(tool_type):
    tools_data = load_tools_from_file("tools.json")
    tools = tools_data["tools"]
    return [tool["name"] for tool in tools if tool["type"] == tool_type]