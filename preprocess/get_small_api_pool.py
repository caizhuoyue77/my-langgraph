import json

# 从query.json文件读取JSON数据
def load_json_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 从train.query.txt读取内容并构建 query_id 到 query 的映射
def load_queries_from_txt(file_path):
    query_map = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                query_id, query_text = parts
                query_map[int(query_id)] = query_text
    return query_map

# 提取API列表并去重
def extract_apis_by_query_ids(json_data, query_ids):
    api_set = set()  # 使用集合来确保唯一性
    unique_apis = []

    for entry in json_data:
        if entry.get('query_id') in query_ids:  # 只匹配存在于query_ids中的条目
            for api in entry.get("api_list", []):
                api_key = f"{api['tool_name']}-{api['api_name']}"  # 使用tool_name和api_name的组合作为唯一标识
                if api_key not in api_set:
                    api_set.add(api_key)
                    unique_apis.append(api)

    return unique_apis

# 将去重后的API列表保存为一个JSON文件
def save_json_to_file(data, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

# 主程序
def main():
    json_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/train.json'   # 输入query.json文件路径
    txt_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/train.query.txt'  # 输入train.query.txt文件路径
    output_file_path = '/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/unique_1k_apis.json'   # 输出文件路径

    # 读取JSON数据
    json_data = load_json_from_file(json_file_path)

    # 读取train.query.txt数据，获取query_id到query_text的映射
    query_map = load_queries_from_txt(txt_file_path)

    # 获取所有query_id
    query_ids = set(query_map.keys())

    # 根据query_ids提取去重后的API列表
    filtered_api_list = extract_apis_by_query_ids(json_data, query_ids)
    
    print(f"API列表中包含 {len(filtered_api_list)} 个API")

    # 保存去重后的API列表到输出文件
    save_json_to_file(filtered_api_list, output_file_path)

    print(f"基于train.query.txt中的query_id，去重后的API列表已保存到 {output_file_path}")

if __name__ == "__main__":
    main()