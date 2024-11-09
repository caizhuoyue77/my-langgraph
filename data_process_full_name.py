import json
import re

import re

def get_api_fullname(s):
    # 删除开头结尾的空格
    s = s.strip()
    # 将所有不是数字、字母、下划线的符号替换为下划线
    return re.sub(r'[^\w]+', '_', s.lower())

def add_full_name(data):
    for obj in data:
        api_name_cleaned = get_api_fullname(obj['api_name'])
        tool_name_cleaned = get_api_fullname(obj['tool_name'])
        obj['full_name'] = f"{api_name_cleaned}_for_{tool_name_cleaned}"
    return data

def process_file(input_file, output_file):
    # Read data from the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Process the data
    processed_data = add_full_name(data)
    
    # Write the processed data to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, indent=4)

# Specify the input and output file paths
input_file = '/Users/caizhuoyue/Desktop/my-langgraph/rapidapi_all_apis.json'  # <-- update this path
output_file = '/Users/caizhuoyue/Desktop/my-langgraph/rapidapi_all_apis_fullname.json'  # <-- update this path

# Process the file
process_file(input_file, output_file)
