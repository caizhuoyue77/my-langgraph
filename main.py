"""
main.py
主模块：根据用户选择的编排方式和模型类型，逐条处理数据并将结果追加保存到指定文件。
"""

import argparse
import json
import os
import time

from vanilla import Vanilla
from react import ReAct
from cot import COT
from reflexion import Reflexion
from dfsdt import DFSDT
from task_decomposer import Decomposer
from czynet import CzyNet


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="任务分解及模型选择脚本")

    # 添加参数：模型类型、编排方式、温度、数据集地址、输出地址
    parser.add_argument(
        "--model",
        type=str,
        choices=["gpt3.5", "qwen2.5:7b", "llama3"],
        required=True,
        help="选择使用的模型类型",
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=["vanilla", "cot", "react", "dfsdt", "reflexion", "ours"],
        required=True,
        help="选择使用的任务编排方式",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="生成文本时的温度值，浮点数，默认值为0.7",
    )
    parser.add_argument(
        "--dataset_path", type=str, required=True, help="数据集文件路径"
    )
    parser.add_argument(
        "--output_path", type=str, required=True, help="输出结果保存的路径"
    )

    return parser.parse_args()


def validate_args(args):
    """参数前置检查"""
    # 检查温度值是否在合理范围内
    if not (0.0 <= args.temperature <= 1.0):
        raise ValueError(f"温度值 ({args.temperature}) 不在合法范围内 [0.0, 1.0]")

    # 检查数据集文件路径是否存在
    if not os.path.isfile(args.dataset_path):
        raise FileNotFoundError(f"指定的数据集文件不存在：{args.dataset_path}")

    print("参数检查通过")


def load_benchmark_data(dataset_path: str):
    """加载基准数据集"""
    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"成功加载数据集：{dataset_path}")
        return data
    except FileNotFoundError:
        raise RuntimeError(f"无法找到数据集文件：{dataset_path}")
    except json.JSONDecodeError:
        raise RuntimeError(f"数据集文件格式错误：{dataset_path}")
    except Exception as exc:
        raise RuntimeError(f"加载数据时发生未知错误：{exc}") from exc


def validate_dataset(data):
    """数据集格式前置检查"""
    if not isinstance(data, list):
        raise ValueError("数据集格式错误：数据集应为包含字典对象的列表")

    for idx, item in enumerate(data):
        if not isinstance(item, dict) or "query" not in item:
            raise ValueError(
                f"数据集格式错误：第 {idx + 1} 条数据不包含必要的 'query' 字段或数据类型错误"
            )
    print(f"数据集检查通过，总计 {len(data)} 条任务数据")


def process_data(data, model: str, method: str, temperature: float, output_path: str):
    """根据选择的模型和编排方式逐条处理数据，并将结果逐条保存"""
    print(f"当前模型：{model}")
    print(f"当前编排方式：{method}")
    print(f"温度参数：{temperature}")
    print(f"当前模式：{method}")

    # 遍历数据集的每一条数据，并根据选择的模式进行处理
    for idx, item in enumerate(data):
        try:
            decomposer = Decomposer(model_name=model, query=item["query"])
            sub_tasks = decomposer.run()
            results = []

            for sub_task in sub_tasks:
                # 根据不同的模式选择对应的处理逻辑
                sub_query = sub_task["description"]
                category = sub_task["category"]

                if method == "react":
                    # 使用 ReAct 模式进行处理
                    react_instance = ReAct(
                        model_name=model, query=sub_query, category=category
                    )
                    result = react_instance.run()
                    
                elif method == "cot":
                    print("main:开始CoT方法！")
                    cot_instance = COT(
                        model_name=model, query=sub_query, category=category
                    )
                    result = cot_instance.run()
                elif method == "vanilla":
                    vanilla_instance = Vanilla(
                        model_name=model, query=sub_query, category=category
                    )
                    result = vanilla_instance.run()
                elif method == "reflexion":
                    reflexion_instance = Reflexion(
                        model_name=model, query=sub_query, category=category
                    )
                    result = reflexion_instance.run()
                elif method == "dfsdt":
                    dfsdt_instance = DFSDT(
                        model_name=model, query=sub_query, category=category
                    )
                    result = dfsdt_instance.run()
                elif method == "ours":
                    # 使用我们自己的模型进行处理
                    czynet_instance = CzyNet(max_api_count = 1)
                    result = czynet_instance.run(query=sub_query, category=category)
                
                results.extend(result)

            # result应该是一个字典，一个运行结果
            # 除了整体的计划，还包括：
            # 计算token消耗
            # 计算时间开销
            # 计算api个数
            # 是否需要实时计算pass rate呢

            # 每处理一条数据就立即保存到输出文件中
            save_result(results, output_path)
            print(f"第 {idx + 1} 条数据处理成功")
            

        except Exception as exc:
            print(f"第 {idx + 1} 条数据处理失败，错误信息：{exc}")


def save_result(result, output_path: str):
    """逐条追加保存结果到指定文件"""
    try:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
        print(f"已保存一条结果至：{output_path}")
    except Exception as exc:
        raise RuntimeError(f"保存结果时发生错误：{exc}") from exc


def main():
    """主函数"""
    args = parse_args()

    # 1. 检查参数合法性
    validate_args(args)

    # 2. 加载并检查数据集
    data = load_benchmark_data(args.dataset_path)
    validate_dataset(data)

    # 3. 根据选择的模式和模型逐条处理数据并逐条保存
    process_data(data, args.model, args.method, args.temperature, args.output_path)


if __name__ == "__main__":
    main()