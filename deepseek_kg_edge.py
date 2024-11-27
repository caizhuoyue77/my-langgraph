import csv
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

import csv
import sys



# 配置 DeepSeek API
API_KEY = "sk-eb93b1c0ba2542239ac5a7ae8aba98ac"  # 替换为你的 DeepSeek API 密钥
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# 初始化 API 客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 测试模式变量
IS_TEST = False  # 设置为 True 以启用测试模式，仅处理一组数据

def read_csv(file_path):
    """读取 CSV 文件并返回数据"""
    # 增加字段大小限制
    csv.field_size_limit(sys.maxsize)  # 设置为系统允许的最大值
    
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def generate_combinations(input_csv):
    """从 API 数据生成所有两两组合"""
    rows = read_csv(input_csv)
    combinations = []

    # 遍历生成所有两两组合
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            combinations.append((rows[i], rows[j]))

    return combinations

def format_api_details(api):
    """格式化 API 的详细信息"""
    return "\n".join([f"{key}: {api.get(key, 'N/A')}" for key in [
       "tool_name", "tool_description", 
        "api_name", "api_url", "required_parameters", 
        "test_endpoint", "api_description", "api_endpoint",
    ]])
    
import re  # 新增导入 re 模块

def extract_outer_json(response_str):
    """
    从 response_str 中提取最外层的 JSON 对象。
    """
    try:
        # 使用正则表达式匹配最外层的 JSON 对象
        match = re.search(r'\{.*\}', response_str, re.DOTALL)
        if match:
            return match.group(0)
        else:
            raise ValueError("未找到有效的 JSON 对象")
    except Exception as e:
        print(f"提取 JSON 出错: {e}")
        raise

def call_deepseek(api_1, api_2):
    """调用 DeepSeek API 获取 API 参数依赖关系"""
    prompt = (
        f"以下是两组 API 数据，请根据它们的名称和描述分析它们之间的参数依赖关系，并输出 JSON 格式的结果。\n"
        f"要求包含以下两部分：\n"
        f"1. 可能有的参数依赖（比如第一个工具的输出是第二个工具的输入）：列出在 API 1 和 API 2 中依赖的参数及其对应名称。\n"
        f"2. 参数依赖描述：一句话解释该参数表示什么。\n\n"
        f"API 信息介绍：test_endpoint 字段表示 API 的输出，required_parameters 表示 API 的输入。\n"
        f"第一组 API:\n"
        f"{format_api_details(api_1)}\n\n"
        f"第二组 API:\n"
        f"{format_api_details(api_2)}\n\n"
        f"举例：假设 API 1 的输出可以作为 API 2 的输入，那么如下：\n"
        f"输出格式：{{\"related_parameters\":[{{\"name_in_first_api（输出在前）\":\"value\",\"name_in_second_api（输入在后）\":\"value\",\"description\":\"This parameter represents...\"}}]}}\n"
        f"若不存在，返回空 JSON 即可。"
    )

    messages = [
        {"role": "system", "content": "You are an expert in building and using APIs"},
        {"role": "user", "content": prompt}
    ]

    try:
        # 调用 DeepSeek API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=False
        )
        
        response_str = response.choices[0].message.content
        print(f"原始响应内容:\n{response_str}")
        
        # 提取最外层 JSON 对象
        json_content = extract_outer_json(response_str)
        
        # 加载为 Python 对象
        result = json.loads(json_content)

        # 提取 dependency 信息
        related_parameters = result.get("related_parameters", [])
        dependency_description = result.get("dependency_description", "N/A")

        # 返回展平后的结构化结果
        return {
            "api_1_tool_name": api_1["tool_name"],
            "api_2_tool_name": api_2["tool_name"],
            "api_1_name": api_1["api_name"],
            "api_2_name": api_2["api_name"],
            "api_1": api_1["hash_id"],
            "api_2": api_2["hash_id"],
            "related_parameters": json.dumps(related_parameters, ensure_ascii=False),
            "dependency_description": dependency_description
        }
        
    except Exception as e:
        print(f"调用 DeepSeek 出错: {e}")
        return None

def process_combinations(input_csv, output_csv):
    """生成组合并调用 DeepSeek"""
    combinations = generate_combinations(input_csv)

    # 定义 CSV header
    headers = [
        "api_1_tool_name", "api_2_tool_name",
        "api_1_name", "api_2_name",
        "api_1", "api_2",
        "related_parameters", "dependency_description"
    ]

    # 测试模式逻辑
    if IS_TEST:
        print("测试模式启用，仅处理一组组合数据...")
        api_1, api_2 = combinations[0]
        result = call_deepseek(api_1, api_2)
        print("测试结果:", json.dumps(result, ensure_ascii=False, indent=4))
        return  # 测试模式直接返回

    results = []
    combination_count = len(combinations)

    # 并行调用
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(call_deepseek, api_1, api_2) for api_1, api_2 in combinations]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                # 实时写入文件
                append_to_csv(output_csv, [result], headers=headers)

    print(f"并行调用完成，共处理 {combination_count} 组组合。")

def append_to_csv(file_path, data, headers):
    """将数据追加到 CSV 文件"""
    file_exists = False
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            file_exists = True
    except FileNotFoundError:
        pass
    
    with open(file_path, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not file_exists:  # 如果文件不存在，写入表头
            writer.writeheader()
        writer.writerows(data)
        
# 输入和输出文件路径
input_csv = "data/small_apis_movies_music.csv"  # 输入的 API 数据文件
output_results_csv = "data/deepseek_edges.csv"  # DeepSeek 分析结果文件

# 执行处理
process_combinations(input_csv, output_results_csv)