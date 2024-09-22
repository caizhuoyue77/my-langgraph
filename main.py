import json
import re
from make_api_plan import get_plan_for_dataset
from judge_pass_rate import get_pass_score
from search_on_graph import get_clusters


# 定义全局变量
API_LIST = [
    "myPlayvv",  # Music sharing service
    "L-yrics API",  # Main endpoint to get song lyrics
    "SpeechNoted API",  # Text to Speech
    "Billboard API",  # Billboard charts API for various music charts
    "weather"  # Weather-related API
]

CLUSTERS = [
    {
        "cluster_id": 1,
        "name": "Music Cluster",
        "summary": "该集群包含与音乐相关的API，提供音乐共享和歌词获取的功能。",
        "apis": [
            {
                "name": "myPlayvv",
                "description": "音乐共享服务"
            },
            {
                "name": "L-yrics API",
                "description": "获取歌曲歌词的主要端点",
                "parameters": [
                    {"name": "song", "description": "歌曲名称的查询参数"},
                    {"name": "artist", "description": "艺术家名称的查询参数"}
                ]
            }
        ]
    },
    {
        "cluster_id": 2,
        "name": "Speech and Text Cluster",
        "summary": "该集群提供文本转语音的API，支持多种语音选项。",
        "apis": [
            {
                "name": "SpeechNoted API",
                "description": "文本转语音服务"
            },
            {
                "name": "Get Voices",
                "description": "获取可用的语音选项",
                "parameters": [
                    {"name": "Voice", "description": "不同语音音调的表示"}
                ]
            }
        ]
    },
    {
        "cluster_id": 3,
        "name": "Billboard Charts Cluster",
        "summary": "该集群提供与Billboard音乐排行榜相关的API，支持多种国家的歌曲榜单。",
        "apis": [
            {
                "name": "Billboard API",
                "description": "提供各种音乐排行榜的API",
                "endpoints": [
                    {"name": "Bolivia Songs", "description": "玻利维亚歌曲排行榜API端点"},
                    {"name": "Slovakia Songs", "description": "斯洛伐克歌曲排行榜API端点"}
                ]
            }
        ]
    },
    {
        "cluster_id": 4,
        "name": "Weather Cluster",
        "summary": "该集群提供与天气相关的API，支持天气查询功能。",
        "apis": [
            {
                "name": "weather",
                "description": "与天气信息相关的API",
                "endpoints": [
                    {"name": "查询天气", "description": "查询天气信息的API节点"}
                ]
            }
        ]
    }
]


def main():
    """
    主函数，处理test.jsonl中的query，生成计划并计算pass rate。
    """
    # 打开输入文件
    with open('data/test1.jsonl', 'r', encoding='utf-8') as infile:
        with open('data/output_plans.jsonl', 'w', encoding='utf-8') as plan_file, \
             open('data/output_scores.jsonl', 'w', encoding='utf-8') as score_file:
            
            # 逐行读取文件
            for line in infile:
                try:
                    # 解析JSON行
                    data = json.loads(line)
                    query = data.get('query', '')

                    # 获取计划
                    plan = pipeline(query)

                    # 将计划写入文件
                    plan_output = {
                        "query": query,
                        "plan": plan.get('plan', ""),
                        "api_calls": plan.get('api_calls', [])
                    }
                    
                    # 定义正则表达式模式
                    REGEX_PATTERN = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*(?:\[(.*?)\])?"
                    
                    # 通过正则表达式提取信息
                    match = re.search(REGEX_PATTERN, plan_output['plan'])
                    if match:
                        extracted_plan = {
                            "action": match.group(1),  # 提取动作
                            "endpoint": match.group(3),  # 提取API端点
                            "params": match.group(4)  # 提取参数
                        }
                    else:
                        extracted_plan = {}

                    # 将提取的计划写入文件
                    plan_file.write(json.dumps({"query": query, "extracted_plan": extracted_plan}) + '\n')
                    
                    # 获取pass rate
                    pass_score = get_pass_score(query, plan_output["plan"])
                    
                    if "pass" in pass_score:
                        pass_score = 1
                    else:
                        pass_score = 0
                        
                    score_output = {
                        "query": query,
                        "plan": plan_output["plan"],
                        "pass_score": pass_score
                    }
                    score_file.write(json.dumps(score_output) + '\n')

                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                except KeyError as e:
                    print(f"字段缺失: {e}")
                except Exception as exc:
                    print(f"未知错误: {exc}")


def pipeline(query: str):
    """
    根据输入的query，执行生成API调用计划并返回结果。
    
    参数:
        query (str): 查询文本
    
    返回:
        dict: 包含query和生成计划的字典
    """
    try:
        # Step 1: 从图谱上搜索相关的API集合
        top_k = 3  # 选择最相关的3个clusters
        selected_clusters = get_clusters(query, CLUSTERS, top_k)
        
        print(f"selected_cluster:{selected_clusters}")
        
        related_apis = [api for cluster in selected_clusters for api in cluster.get('apis', [])]
        
        print(f"related_apis:{related_apis}")

        # Step 2: 使用相关的API生成计划
        plans = get_plan_for_dataset([query], related_apis)
        
        # Step 3: 返回第一个生成的计划
        return plans[0] if plans else {"query": query, "plan": "", "api_calls": []}
    
    except Exception as e:
        print(f"生成计划时出现错误: {e}")
        return {"query": query, "plan": "", "api_calls": []}


if __name__ == '__main__':
    main()
