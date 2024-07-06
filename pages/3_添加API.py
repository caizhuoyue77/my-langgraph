import streamlit as st

# 添加固定的 logo
logo_url = "https://www.google.com/imgres?q=chickfila%20logo&imgurl=https%3A%2F%2Flogos-world.net%2Fwp-content%2Fuploads%2F2021%2F08%2FChick-fil-A-Logo.png&imgrefurl=https%3A%2F%2Flogos-world.net%2Fchick-fil-a-logo%2F&docid=PTolwfZA_mMR2M&tbnid=btCR2wq2V8ejeM&vet=12ahUKEwiq-5an4pGHAxUfr1YBHfXtDKsQM3oECBcQAA..i&w=3840&h=2160&hcb=2&ved=2ahUKEwiq-5an4pGHAxUfr1YBHfXtDKsQM3oECBcQAA"  # 替换为你的 logo URL
st.markdown(
    f"""
    <style>
    .fixed-logo {{
        position: fixed;
        top: 10px;
        right: 10px;
        width: 100px;  # 根据需要调整 logo 的大小
    }}
    </style>
    <img src="{logo_url}" class="fixed-logo">
    """,
    unsafe_allow_html=True,
)


def main():
    st.title("API 请求配置")

    # 输入框：API 端点
    api_endpoint = st.text_input(
        "API Endpoint", placeholder="例如：https://api.example.com/data"
    )

    # 下拉框：请求方式
    request_method = st.selectbox("请求方式", ["GET", "POST", "DELETE", "PUT"])

    # 输入框：API 密钥
    api_key = st.text_input("API Key", placeholder="请输入您的API密钥")

    # 动态添加 API 参数
    st.subheader("API 参数")
    params = {}
    if "param_count" not in st.session_state:
        st.session_state.param_count = 0

    param_count = st.session_state.param_count

    for i in range(param_count):
        key = st.text_input(f"参数名 {i+1}", key=f"param_key_{i}")
        value = st.text_input(f"参数值 {i+1}", key=f"param_value_{i}")
        params[key] = value

    if st.button("添加参数"):
        st.session_state.param_count += 1

    # 显示配置
    st.subheader("配置预览")
    st.write("API Endpoint:", api_endpoint)
    st.write("请求方式:", request_method)
    st.write("API Key:", api_key)
    st.write("API 参数:", params)

    # 发送请求按钮
    if st.button("发送请求"):
        st.write("模拟发送请求...")  # 这里可以添加发送请求的代码


if __name__ == "__main__":
    main()
