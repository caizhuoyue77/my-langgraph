import json

def get_tool_list_str():
    with open("tools.json", "r") as f:
        tool_list = json.load(f)
        tool_list_str = "\n".join([
            f"({i+1}) {tool['name']}[{tool['input']}]: {tool['description']}"
            for i, tool in enumerate(tool_list["tools"])
        ])
        return tool_list_str