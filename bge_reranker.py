from FlagEmbedding import FlagReranker
reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True) # Setting use_fp16 to True speeds up computation with a slight performance degradation

def get_reranker_similarity_score(query:str, key:str):
    # 通过RAG，只获取直接有关的
    score = reranker.compute_score([query, key])
    return score


def bge_reranker_best_keys(query:str, memory: dict, top_k:int=3):
    filteredmemory = {}

    to_calc = []
    for key in memory:
        to_calc.append([query, key])
    scores = reranker.compute_score(to_calc)

    # 对scores进行排序，取top_k
    sorted_scores = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

    for i in range(min(top_k, len(sorted_scores))):
        idx, score = sorted_scores[i]
        key = to_calc[idx][1]
        filteredmemory[key] = memory[key]
        print(f"key:{key}, score:{score}")
    
    print(filteredmemory)
    return filteredmemory