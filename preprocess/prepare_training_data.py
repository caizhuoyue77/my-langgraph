import json
import random

def process_json_file(input_file_path, output_file_path, neg_file_path):
    sum_len = 0
    # 1. 读取 JSON 文件
    with open(input_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 2. 读取 neg 字段 API 文件
    with open(neg_file_path, 'r', encoding='utf-8') as neg_file:
        neg_data = json.load(neg_file)

    # 随机选择两个 API 对象
    if len(neg_data) < 2:
        raise ValueError("API 数据不足以选择两个对象。")

    processed_data = []
    idx = 0
    for item in data:
        query = item.get('query')
        api_list = item.get('api_list', [])

        # 判断 query 是否为字符串
        if not isinstance(query, str):
            continue  # 如果不是字符串，跳过此条数据

        # 3. 仅保留 category_name, tool_name, api_name 和 api_description
        api_strings = []
        for api in api_list:
            api_string = f"{api['category_name']} {api['tool_name']} - {api['api_name']}: {api['api_description']}"
            api_strings.append(api_string)

        # 4. 形成新的 JSON 结构
        new_object = {
            "query": query,
            "pos": api_strings,
            "neg": [f"{api['category']} {api['tool_name']} - {api['api_name']}: {api['api_description']}" 
                    for api in random.sample(neg_data, 2)]
        }
        sum_len += len(query)
        processed_data.append(new_object)
        idx += 1
        print(idx)

    # 5. 将结果写入 JSON Lines 文件
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for obj in processed_data:
            output_file.write(json.dumps(obj, ensure_ascii=False) + '\n')

    avg_len = sum_len / idx if idx > 0 else 0
    print(avg_len)

# 使用示例
input_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/train.json'  # 替换为你的输入文件路径
output_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/sft.jsonl'  # 替换为你的输出文件路径
neg_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/rapidapi_all_apis.json'  # 替换为你的 neg API 文件路径

process_json_file(input_file_path, output_file_path, neg_file_path)

print(f"处理完成，结果已保存到 {output_file_path}")