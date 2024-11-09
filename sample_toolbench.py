import json
import random

def sample_json_objects(input_file: str, output_file: str, sample_size: int) -> None:
    """
    从给定的 JSON 文件中抽样 k 个 JSON 对象，并将其保存到新的 JSON 文件中。

    参数:
    - input_file (str): 输入 JSON 文件的路径。
    - output_file (str): 输出 JSON 文件的路径。
    - sample_size (int): 要抽样的对象数量。
    """

    try:
        # 读取 JSON 文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 检查数据是否为列表
        if not isinstance(data, list):
            raise ValueError("JSON 文件格式不正确，应该是一个对象列表")

        # 确保 sample_size 不超过数据的长度
        if sample_size > len(data):
            raise ValueError(f"要求的样本数量 {sample_size} 超过了可用对象的数量 {len(data)}")

        # 随机抽样 k 个 JSON 对象
        sampled_objects = random.sample(data, sample_size)

        # 将结果写入新的 JSON 文件
        
        # 删除一些额外的参数
        for obj in sampled_objects:
            for api in obj['api_list']:
                del api['required_parameters']
                if 'template_response' in api:
                    del api['template_response']
                del api['method']
                del api['optional_parameters']
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sampled_objects, f, ensure_ascii=False, indent=4)

        print(f"成功从 {input_file} 中抽样 {sample_size} 个对象，并保存到 {output_file}")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
    except json.JSONDecodeError:
        print(f"错误: 无法解码 JSON 文件 {input_file}")
    except ValueError as e:
        print(f"错误: {e}")
    except Exception as exc:
        print(f"发生错误: {exc}")


# 示例用法
if __name__ == "__main__":
    INPUT_FILE = '/Users/caizhuoyue/Desktop/my-langgraph/data/instruction/G1_query.json'  # 输入文件路径
    OUTPUT_FILE = '/Users/caizhuoyue/Desktop/my-langgraph/data/instruction/G1_query_sample_10.json'  # 输出文件路径
    SAMPLE_SIZE = 10  # 要抽样的数量

    sample_json_objects(INPUT_FILE, OUTPUT_FILE, SAMPLE_SIZE)