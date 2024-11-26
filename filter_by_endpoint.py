import json

# 从文件中加载原始数据
with open('data/filtered_tools.json', 'r', encoding='utf-8') as f:
    apis_data = json.load(f)

# 筛选掉不符合条件的API对象
filtered_apis = []

for api in apis_data:
    filtered_api_list = []

    for api_item in api['api_list']:
        # 获取 test_endpoint 字段
        test_endpoint = api_item.get('test_endpoint')

        # 判断 test_endpoint 是否为字符串、只有一个键的字典，或者是一个列表
        if isinstance(test_endpoint, str) or \
           (isinstance(test_endpoint, dict) and len(test_endpoint) == 1) or \
           isinstance(test_endpoint, list):
            continue  # 如果是字符串、单键字典或列表，跳过此API项
        
        # 如果 test_endpoint.message 为 "You are not subscribed to this API."，则跳过
        if test_endpoint and test_endpoint.get('message') == "You are not subscribed to this API.":
            continue  # 跳过此API项

        # 如果通过筛选条件，保留该API项
        filtered_api_list.append(api_item)
    
    # 如果筛选后的列表非空，则保留该API
    if filtered_api_list:
        api['api_list'] = filtered_api_list
        filtered_apis.append(api)

# 将筛选后的数据导出到 filteredx4_apis.json 文件
with open('data/filteredx4_apis.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_apis, f, ensure_ascii=False, indent=4)

print("筛选后的数据已保存为 filteredx4_apis.json")
