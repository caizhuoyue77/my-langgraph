import streamlit as st
import pandas as pd
import json
from st_aggrid import AgGrid, GridOptionsBuilder


def read_tools(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["tools"]


def format_tools(tools_info):
    formatted_data = []
    for tool in tools_info:
        formatted_data.append(
            {
                "ID": tool["id"],
                "名称": tool["name"],
                "标签": tool["label"],
                "输入": tool["input"],
                "描述": tool["description"],
                "类型": tool["type"],
                "幂等性": tool["idempotency"],
            }
        )
    return formatted_data


def add_logo():
    logo_path = "assets/images/logo.jpeg"  # 本地logo图片路径
    st.image(logo_path, width=100)


def main():
    add_logo()

    st.title("工具信息展示")

    # 读取工具信息
    tools_info = read_tools("tools.json")
    formatted_data = format_tools(tools_info)

    # 转换为 DataFrame
    df = pd.DataFrame(formatted_data)

    # 使用 AgGrid 显示表格
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationPageSize=15)  # 每页显示15个
    gb.configure_side_bar()  # 添加侧边栏
    grid_options = gb.build()

    AgGrid(
        df,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        theme="alpine",  # 其他主题： 'balham', 'material'
        height=600,
        fit_columns_on_grid_load=True,
    )


if __name__ == "__main__":
    main()
