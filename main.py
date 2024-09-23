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

REGEX_PATTERN = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*(?:\[(.*?)\])?"

def main():
    """主函数，处理test.jsonl中的query，生成计划并计算pass rate。"""
    with open('data/test1.jsonl', 'r', encoding='utf-8') as infile:
        with open('data/output_plans.jsonl', 'w', encoding='utf-8') as plan_file, \
             open('data/output_scores.jsonl', 'w', encoding='utf-8') as score_file:
             
            for line in infile:
                try:
                    data = json.loads(line)
                    query = data.get('query', '')
                    plan = pipeline(query)

                    # 提取步骤
                    steps = extract_steps(plan['plan'])
                    plan_output = {
                        "query": query,
                        "plan": plan.get('plan', ""),
                        "api_calls": steps
                    }
                    plan_file.write(json.dumps(plan_output, ensure_ascii=False) + '\n')

                    # 获取pass rate
                    pass_rate = get_pass_score(query, plan["plan"])
                    pass_score = 1 if "pass" in pass_rate else 0

                    # 打印结果
                    print_plan(query, plan, pass_rate, pass_score)

                    score_output = {
                        "query": query,
                        "plan": plan,
                        "pass_rate": pass_rate,
                        "pass_score": pass_score
                    }
                    score_file.write(json.dumps(score_output, ensure_ascii=False) + '\n')

                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                except KeyError as e:
                    print(f"字段缺失: {e}")
                except Exception as exc:
                    print(f"未知错误: {exc}")

def extract_steps(plan_string: str):
    """通过正则表达式提取计划步骤。"""
    matches = re.findall(REGEX_PATTERN, plan_string)
    return matches

def pipeline(query: str):
    """根据输入的query，执行生成API调用计划并返回结果。"""
    try:
        top_k = 3
        selected_clusters = get_clusters(query, CLUSTERS, top_k)
        related_apis = [api for cluster in selected_clusters for api in cluster.get('apis', [])]
        plans = get_plan_for_dataset([query], related_apis)
        return plans[0] if plans else {"query": query, "plan": "", "api_calls": []}
    
    except Exception as e:
        print(f"生成计划时出现错误: {e}")
        return {"query": query, "plan": "", "api_calls": []}

def print_plan(query: str, plan: dict, pass_rate : str, pass_score: int):
    """以美观的方式打印计划和评分信息"""
    print("\n" + "=" * 40)
    print(f"查询: {query}")
    print(f"计划: {plan.get('plan', '无计划')}")
    
    print("API 调用:")

    if plan.get('api_calls'):
        for idx, step in enumerate(plan['api_calls']):
            print(f"step {idx + 1}")  # idx + 1 使步骤编号从1开始
            print(f"  - 名称: {step['name']}")
            print(f"    描述: {step['description']}")
    else:
        print("  无API调用")

    print(f"测评结果: {pass_rate}")
    print(f"得分: {pass_score}")
    print("=" * 40 + "\n")

if __name__ == '__main__':
    main()
