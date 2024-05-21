from FlagEmbedding import BGEEmbedding

model_path = '/nvme/lisongling/models/bge-base-zh-v1.5'

model = BGEEmbedding(model_path)

def get_similarity_score(query:str, key:str):
    # 通过RAG，只获取直接有关的
    q_embeddings = model.get_embedding(query)
    p_embeddings = model.get_embedding(key)
    score = BGEEmbedding.cosine_similarity(q_embeddings, p_embeddings)
    return score

def bge_best_keys(query:str, memory:dict, threshold: float = 0.4):
    filtered_memory = {}

    for key in memory:
        print(query,key)
        score = get_similarity_score(query, key)
        if score > threshold:
            filtered_memory[key] = memory[key]
            print(f"key:{key}, score:{score}")
    return filtered_memory

if __name__ == '__main__':
    print(get_similarity_score("你想去吃点什么呀？","喜欢的食物"))