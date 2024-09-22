from openai import OpenAI
import tiktoken
from typing import Optional

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    计算文本在指定模型中的token数量。

    Args:
        text (str): 需要计算的文本
        model (str): 使用的模型名称，默认是 "gpt-3.5-turbo"

    Returns:
        int: 文本中的token数量
    """
    try:
        encoder = tiktoken.encoding_for_model(model)
    except KeyError as e:
        raise ValueError(f"无效的模型名称: {model}, 错误信息: {e}")

    tokens = encoder.encode(text)
    return len(tokens)

def get_chat_response(prompt: str) -> Optional[str]:
    """
    使用 OpenAI API 获取聊天回复。

    参数:
    prompt (str): 要发送到聊天模型的提示语

    返回:
    Optional[str]: 模型生成的回复内容。如果发生错误，返回 None。
    """
    # 初始化 OpenAI 客户端
    try:
        client = OpenAI(
            api_key="sk-H0UFSY3LvO8YBt092HnMfLO6oRHZjbwdwTVucnxRwVEUzZAA",
            base_url="https://api.chatanywhere.tech/v1"
            # base_url="https://api.chatanywhere.cn/v1"
        )
    except Exception as e:
        print(f"初始化 OpenAI 客户端时出错: {e}")
        return None

    # 调用 chat.completions.create 方法
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            # response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
    except Exception as e:
        print(f"调用 OpenAI API 时出错: {e}")
        return None

    # 提取并返回 response 中的 content 字段
    try:
        content = response.choices[0].message.content if response.choices else "No content available"
        return content
    except AttributeError as e:
        print(f"解析 API 响应时出错: {e}")
        return None