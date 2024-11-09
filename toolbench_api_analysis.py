import json
from collections import Counter

def find_duplicate_api_names(json_file_path: str) -> None:
    """
    查找JSON文件中重复的api_name，并输出重复项及其出现次数。
    
    :param json_file_path: JSON文件的路径
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 检查数据类型是否为列表
        if not isinstance(data, list):
            raise ValueError(f"数据格式不正确，应为list，但检测到{type(data)}")

        # 统计相同的api_name数量
        api_name_counter = Counter(tool['api_name'] for tool in data if 'api_name' in tool)

        # 筛选出重复的api_name
        duplicate_api_names = {api_name: count for api_name, count in api_name_counter.items() if count > 1}

        # 输出结果
        print("重复的api_name及其出现次数：")
        if duplicate_api_names:
            for api_name, count in duplicate_api_names.items():
                print(f"{api_name}: {count} 次")
        else:
            print("没有重复的api_name。")

    except FileNotFoundError:
        print(f"文件 {json_file_path} 未找到，请检查路径是否正确。")
    except json.JSONDecodeError:
        print(f"文件 {json_file_path} 解析失败，请检查JSON格式是否正确。")
    except Exception as e:
        print(f"出现错误：{e}")

# 调用函数，传入JSON文件路径
json_file_path = "/Users/caizhuoyue/Desktop/my-langgraph/rapidapi_all_apis.json"  # 请将此处替换为你的JSON文件路径
find_duplicate_api_names(json_file_path)