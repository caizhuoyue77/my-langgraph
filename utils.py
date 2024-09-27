import json
import os

def filter_api_by_category(json_file: str, categories: list) -> list:
    """
    从指定的 JSON 文件中读取数据，并根据给定类别筛选 JSON 对象。
    
    :param json_file: str，JSON 文件的名称，必须包含 .json 后缀
    :param categories: list，包含要筛选的类别名称的列表
    :return: list，符合条件的 JSON 对象列表
    """
    # 检查文件是否存在
    if not os.path.isfile(json_file):
        raise FileNotFoundError(f"文件未找到: {json_file}")

    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            # 读取 JSON 数据
            data = json.load(file)
        
        # 筛选符合条件的 JSON 对象
        filtered_data = [item for item in data if item.get('category') in categories]
        return filtered_data

    except json.JSONDecodeError as e:
        raise RuntimeError(f"读取 JSON 文件时出错: {e}")
    except Exception as e:
        raise RuntimeError(f"发生错误: {e}")