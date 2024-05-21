# my-langgraph

## 启动方式：
1. conda activate langgraph
2. fastapi dev api.py（把后端开起来）
3. streamlit run chatbot.py（把前端开起来）

## 简单介绍

1. 实现了2种RAG的方式：
   1. 基于bge（设置threshold为0.45，作为参数可变）
   2. 基于bge-reranker（设置top-k为10，作为参数可变）