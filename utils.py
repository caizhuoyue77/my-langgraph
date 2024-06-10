import json

def load_tools_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        tools_data = json.load(file)
    return tools_data

def get_tool_list_str():
    tools_data = load_tools_from_file("tools_shengqian.json")
    tool_list_str = "\n".join([
        f"({i+1}) {tool['name']}[{tool['input']}]: {tool['description']}"
        for i, tool in enumerate(tools_data["tools"])
    ])
    return tool_list_str

def get_tools_by_type(tool_type):
    tools_data = load_tools_from_file("tools_shengqian.json")
    tools = tools_data["tools"]
    return [tool for tool in tools if tool["type"] == tool_type]

def get_tools_by_types(tool_types):
    print(f"tool_types: {tool_types}")
    tools_list = []
    for tool_type in tool_types:
        tools = get_tools_by_type(tool_type)
        print(tools)
        tools_list.extend(tools)
    print(tools_list)
    return {
        "tools": tools_list,
        "edges": []
    }

if __name__ == '__main__':
    # Example usage of get_tools_by_types with a single type 'entertainment'
    tools_data = get_tools_by_types(["entertainment"])
    print(json.dumps(tools_data, indent=2))
