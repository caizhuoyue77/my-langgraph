from FlagEmbedding import FlagModel

model = FlagModel('BAAI/bge-base-zh-v1.5', 
                  query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                  use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation


def get_similarity_score(query:str, key:str):
    # 通过RAG，只获取直接有关的
    q_embeddings = model.encode_queries([query])
    p_embeddings = model.encode([key])
    score = q_embeddings @ p_embeddings.T
    return score[0]


def bge_best_keys(query:str, memory:dict, threshold: float = 0.45):
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