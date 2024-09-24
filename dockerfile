# 基于python3.10的官方镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制requirements.txt文件到工作目录
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制整个项目文件到工作目录
COPY . .

# 暴露FastAPI和Streamlit的端口
EXPOSE 8000 8501

# 环境变量设置
ENV PYTHONUNBUFFERED=1

# 启动FastAPI后端和Streamlit前端
CMD uvicorn api:app --host 0.0.0.0 --port 8000 & streamlit run chatbot.py --server.address 0.0.0.0 --server.port 8501