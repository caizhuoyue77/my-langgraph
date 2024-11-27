import csv
import json
from openai import OpenAI

# 配置 DeepSeek API
API_KEY = "sk-eb93b1c0ba2542239ac5a7ae8aba98ac"  # 替换为你的 DeepSeek API 密钥
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# 初始化 API 客户端
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# 输入和输出文件
input_csv = "data/api.csv"  # 输入文件
output_csv = "data/deepseek_api_relationships.csv"  # 输出文件

# 大模型返回格式定义
output_format_description = """
请按照以下 JSON 格式返回结果：
{
  "api_1_tool_name": "<第一组 API 的 tool_name>",
  "api_2_tool_name": "<第二组 API 的 tool_name>",
  "similarities": ["<两组 API 的相似点>"],
  "differences": ["<两组 API 的主要不同点>"],
  "relationship": "<两组 API 的关系描述>"
}
"""

def read_csv(file_path):
    """读取 CSV 文件并返回数据"""
    print(f"读取输入文件：{file_path}")
    with open(file_path, mode='r', encoding='utf-8') as file:
        return list(csv.reader(file))

def append_to_csv(file_path, data, headers):
    """将数据追加到 CSV 文件"""
    print(f"将结果追加写入到文件：{file_path}")
    file_exists = False
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            file_exists = True
    except FileNotFoundError:
        print(f"{file_path} 不存在，将创建新文件。")
    
    with open(file_path, mode='a', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not file_exists:  # 如果文件不存在，写入表头
            writer.writeheader()
        writer.writerows(data)

def analyze_rows_difference(row_1, row_2):
    """比较两行数据并调用 DeepSeek API"""
    # 提取所需字段
    tool_name_idx = headers.index("tool_name")
    tool_description_idx = headers.index("tool_description")
    api_description_idx = headers.index("api_description")
    
    row_1_str = (
        f"Tool Name: {row_1[tool_name_idx]}\n"
        f"Tool Description: {row_1[tool_description_idx]}\n"
        f"API Description: {row_1[api_description_idx]}"
    )
    row_2_str = (
        f"Tool Name: {row_2[tool_name_idx]}\n"
        f"Tool Description: {row_2[tool_description_idx]}\n"
        f"API Description: {row_2[api_description_idx]}"
    )

    # 构造提示语
    prompt = (
        f"以下是两组 API 数据，请分析它们的主要区别，并输出 JSON 格式的结果。\n"
        f"{output_format_description}\n"
        f"第一组数据：\n{row_1_str}\n\n"
        f"第二组数据：\n{row_2_str}"
    )

    print(f"向大模型发送请求，比较以下两行：\n{row_1_str}\n---\n{row_2_str}")
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=False
        )
        result = response.choices[0].message.content
        print(f"大模型返回结果：{result}")
        return result
    except Exception as e:
        print(f"调用 DeepSeek API 出错: {e}")
        return None

def parse_and_validate_json(response):
    """解析并验证模型返回的 JSON 格式"""
    try:
        parsed = json.loads(response)
        # 验证必要的字段是否存在
        required_keys = ["api_1_tool_name", "api_2_tool_name", "similarities", "differences", "relationship"]
        if all(key in parsed for key in required_keys):
            print(f"JSON 格式验证通过：{parsed}")
            return parsed
        else:
            print(f"JSON 缺少必要字段: {parsed}")
            return None
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}")
        return None

# 读取输入数据
data = read_csv(input_csv)
headers = data[0]
rows = data[1:]  # 数据部分

# 用于存储分析结果
results = []

# 对每两行进行比较
for i in range(len(rows)):
    for j in range(i + 1, len(rows)):
        print(f"正在比较第 {i+1} 行和第 {j+1} 行...")
        response = analyze_rows_difference(rows[i], rows[j])
        if response:
            parsed_result = parse_and_validate_json(response)
            if parsed_result:
                # 将解析后的数据添加到结果中
                result = {
                    "api_1_tool_name": parsed_result["api_1_tool_name"],
                    "api_2_tool_name": parsed_result["api_2_tool_name"],
                    "similarities": "; ".join(parsed_result["similarities"]),
                    "differences": "; ".join(parsed_result["differences"]),
                    "relationship": parsed_result["relationship"]
                }
                results.append(result)
                # 每次比较完成后立即保存结果
                append_to_csv(output_csv, [result], headers=["api_1_tool_name", "api_2_tool_name", "similarities", "differences", "relationship"])
        else:
            print(f"跳过第 {i+1} 行和第 {j+1} 行的比较，因大模型未返回有效结果。")

print("所有行的比较完成。")