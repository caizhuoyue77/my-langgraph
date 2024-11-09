import json

count = 0

def process_data(embedding_file, query_file):
    global count
    # 读取embedding_bce_1k_results.jsonl 文件
    with open(embedding_file, 'r') as f:
        embedding_data = [json.loads(line) for line in f.readlines()]
    
    # 读取query.json文件
    with open(query_file, 'r') as f:
        query_data = json.load(f)
    
    # 创建一个结果字典
    results = {}

    # 遍历embedding文件的数据
    for embedding_entry in embedding_data:
        query = embedding_entry['query']
        
        # 在query_data中查找匹配的query_id
        matching_query = next((item for item in query_data if item['query'] == query), None)
        
        if matching_query:
            score = 0
            embedding_apis = embedding_entry['result']
            query_apis = matching_query['api_list']
            
            # print('----------start-------------')
            # print(f"query_id:{query_id}")
            # print([item['api_name'] for item in embedding_apis])
            # print([item['api_name'] for item in query_apis])
            # print('-----------end------------')
            
            # 遍历embedding的API列表，查找匹配
            for embedding_api in embedding_apis:
                for query_api in query_apis:
                    if (embedding_api['api_name'] == query_api['api_name'] and 
                        embedding_api['tool_name'] == query_api['tool_name']):
                        score += 1
            
            # 将query_id和分数存入结果
            results[query] = score
    
    # 打印分数
    for query_id, score in results.items():
        if score > 0:
            print(f"Query: {query}, Score: {score}")
            count += 1

# 文件路径
embedding_file = 'tuned_small_embedding_bge-small-en-v1.5_tuned_1k_results_top10.jsonl'
query_file = '/Users/caizhuoyue/Desktop/my-langgraph/data/retrieval/G1/train.json'

# 调用函数
process_data(embedding_file, query_file)

print(count)