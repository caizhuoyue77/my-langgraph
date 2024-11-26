import json

# 定义一个函数来检查字典中是否存在某个键
def check_key_exists(data, key, data_name):
    if key not in data:
        print(f"警告：{data_name} 缺少关键字段：{key}")
        return False
    return True

# 定义排除的字段
exclude_fields = {'name', 'id', 'url'}

# 从文件中加载已筛选的数据
try:
    with open('data/filteredx4_apis.json', 'r', encoding='utf-8') as f:
        filtered_apis = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"加载文件时发生错误: {e}")
    filtered_apis = []

# 存储API之间的依赖关系
api_dependencies = []

# 统计相关数据
total_apis = 0  # API总数
total_tools = 0  # Tool总数（每个api_list对应一个Tool）
matched_api_pairs = 0  # 有参数关系的API对数量

# 遍历每个API对象（每个API对象代表一个Tool）
for api1 in filtered_apis:
    total_tools += 1  # 每个api1代表一个Tool
    
    # 获取Tool的名称
    tool1_name = api1.get('name', '未知Tool')

    # 遍历Tool下的所有API（api_list）
    for api_item1 in api1.get('api_list', []):  # 使用.get()防止不存在key时抛出异常
        total_apis += 1  # 统计每个API
        
        if check_key_exists(api_item1, 'test_endpoint', 'API1'):
            test_endpoint = api_item1['test_endpoint']
            if test_endpoint:  # 如果'test_endpoint'为空，跳过
                # 获取API1的test_endpoint中的所有字段名称
                api1_test_fields = set(test_endpoint.keys())

                # 遍历其他API（api2）进行匹配
                for api2 in filtered_apis:
                    tool2_name = api2.get('name', '未知Tool')  # 获取Tool2的名称
                    for api_item2 in api2.get('api_list', []):  # 使用.get()防止不存在key时抛出异常
                        if check_key_exists(api_item2, 'required_parameters', 'API2'):
                            required_params = api_item2['required_parameters']
                            if required_params:  # 如果'required_parameters'为空，跳过
                                # 获取API2的required_parameters中的字段名称
                                api2_required_params = set(param['name'] for param in required_params if 'name' in param)

                                # 排除掉不参与匹配的字段
                                filtered_api1_test_fields = api1_test_fields - exclude_fields
                                filtered_api2_required_params = api2_required_params - exclude_fields

                                # 找出匹配的字段名称（排除掉不参与匹配的字段）
                                matched_params = filtered_api1_test_fields.intersection(filtered_api2_required_params)

                                # 如果有匹配的字段，检查是否API1和API2的tool_name和name完全相同
                                if matched_params:
                                    if api_item1.get('name') == api_item2.get('name') and tool1_name == tool2_name:
                                        # 如果Tool名称和API名称都相同，则跳过
                                        continue

                                    dependency = {
                                        "api1": {
                                            "name": api_item1.get('name', '未知'),
                                            "tool_name": tool1_name  # API1所属Tool的name
                                        },
                                        "api2": {
                                            "name": api_item2.get('name', '未知'),
                                            "tool_name": tool2_name  # API2所属Tool的name
                                        },
                                        "matched_param": list(matched_params)
                                    }
                                    api_dependencies.append(dependency)
                                    matched_api_pairs += 1  # 统计匹配的API对

# 将依赖关系结果导出到新的JSON文件
try:
    with open('data/api_dependencies.json', 'w', encoding='utf-8') as f:
        json.dump(api_dependencies, f, ensure_ascii=False, indent=4)
    print("API依赖关系已保存到 api_dependencies.json")
except Exception as e:
    print(f"保存依赖关系文件时发生错误: {e}")

# 输出统计信息
print(f"总共的API数量: {total_apis}")
print(f"总共的Tool数量: {total_tools}")
print(f"匹配出的API对数量（有参数关系的）: {matched_api_pairs}")
