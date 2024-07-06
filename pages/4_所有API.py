import streamlit as st
import pandas as pd
import json


def read_api_info(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def format_api_info(api_info):
    formatted_data = []
    for api in api_info:
        endpoint = api["endpoint"]
        api_key = "***" + api["api_key"][-3:]
        added_time = api["added_time"]
        status = "可用" if api["status"] == "active" else "不可用"
        for param in api["params"]:
            formatted_data.append(
                {
                    "Endpoint": endpoint,
                    "参数名": param["name"],
                    "参数类型": param["type"],
                    "示例参数": str(param["example"]),  # 确保示例参数为字符串类型
                    "API Key": api_key,
                    "添加时间": added_time,
                    "状态": status,
                }
            )
    return formatted_data


def add_logo():
    logo_path = "assets/images/logo.jpeg"  # 本地logo图片路径
    st.image(logo_path, width=100)


def main():
    add_logo()

    st.title("API 信息展示")

    # 读取 API 信息
    api_info = read_api_info("api_info.json")
    formatted_data = format_api_info(api_info)

    # 转换为 DataFrame
    df = pd.DataFrame(formatted_data)

    # 显示表格
    st.table(df)


if __name__ == "__main__":
    main()
