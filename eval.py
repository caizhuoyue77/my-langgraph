import json
from pass_rate import PassRate

def process_jsonl(input_file: str, output_file: str):
    """
    处理指定的 jsonl 文件，逐行读取数据并计算 pass_rate，结果写入新的 jsonl 文件。
    
    :param input_file: 输入的 jsonl 文件路径
    :param output_file: 输出的 jsonl 文件路径
    """
    try:
        # 打开输入和输出文件
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            for line in infile:
                # 逐行读取并解析 json 数据
                data = json.loads(line.strip())
                
                # 提取需要传递给 PassRate 的参数
                query = data.get('query', '')
                plan = data.get('plan', [])
                tools = data.get('tools', [])
                final_answer = data.get('final_answer', '')
                
                # 初始化 PassRate 实例并计算 pass_rate
                pass_rate_instance = PassRate(query, plan, tools, final_answer)
                pass_rate = pass_rate_instance.run()

                # 将 pass_rate 添加到当前数据中
                data['pass_rate'] = pass_rate

                # 将修改后的数据写入到输出文件中
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                
            print(f"处理完成，结果已存储到 {output_file}")
    
    except FileNotFoundError as exc:
        raise RuntimeError(f"文件未找到: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 解析错误: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"未知错误: {exc}") from exc

# 示例调用
input_file = 'input.jsonl'
output_file = 'output_with_pass_rate.jsonl'
process_jsonl(input_file, output_file)