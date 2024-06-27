以下是精简和优化后的API文档：

# 历史版本

## 版本命名的建议

1. MAJOR（主版本号）: 当你做了不兼容的API修改时递增。
2. MINOR（次版本号）: 当你做了向下兼容的功能性新增时递增。
3. PATCH（修订号）: 当你做了向下兼容的问题修正时递增。

## 版本1.2.0

**发布日期**: xxxx

**更新功能**:
- 需要把语义节点也加进来，再get_plan里面获取knowledge_graph字段，作为在页面上展示的内容。

## 版本1.1.0 

**发布日期**: 2024-06-22

**初始版本**:
- 实现了`GET /`根端点。
- 实现了`POST /get_plan`端点。
- 实现了`POST /execute_plan`端点。

# API 文档

## 概述

该API基于FastAPI框架，提供两个主要端点来处理计划获取和执行操作。

## 端点一览

1. `GET /` - 根端点，返回欢迎消息。
2. `POST /get_plan` - 接收用户查询，返回计划。
3. `POST /execute_plan` - 接收计划状态，执行计划步骤。

### 1. 根端点

#### `GET /`

**描述**:
返回简单的欢迎消息，用于测试API是否正常工作。

**请求参数**:
无

**响应示例**:
```json
{
    "Hello": "World"
}
```

### 2. 获取计划端点

#### `POST /get_plan`

**描述**:
接收用户查询，返回相应的计划和状态。

**请求参数**:
- `message` (string): 用户的查询消息。

**请求示例**:
```bash
curl -X POST "http://127.0.0.1:8000/get_plan" \
-H "Content-Type: application/json" \
-d '{"message": "最近有哪些热映电影？"}'
```

**响应字段**:
- `response` (string): 自然语言描述的步骤。
- `rewoo_state` (object): 包含计划状态的JSON对象。

**响应示例**:
```json
{
    "response": "API编排步骤：\n1. 使用WeekTop10工具获取当前热门电影列表。",
    "rewoo_state": {
        "task": "任务：搜索最近热映电影",
        "plan_string": "Plan: 使用WeekTop10工具获取当前热门电影列表。\n#E1 = WeekTop10[movies]",
        "steps": [
            ["使用WeekTop10工具获取当前热门电影列表。", "#E1", "WeekTop10", "movies"]
        ],
        "api_recommendations": {
            "nodes": [
                {
                    "id": "fan_favorites",
                    "name": "FanFavorites",
                    "label": "FanFavorites",
                    "input": "query",
                    "description": "获取IMDb上的粉丝喜爱电影或系列。",
                    "type": "entertainment"
                },
                {
                    "id": "search_imdb",
                    "name": "SearchIMDB",
                    "label": "SearchIMDB",
                    "input": "search query",
                    "description": "在IMDb上搜索信息。",
                    "type": "entertainment"
                }
            ],
            "edges": []
        }
    }
}
```

**错误响应**:
- `400 Bad Request`:
  ```json
  {
      "detail": "No query provided"
  }
  ```

### 3. 执行计划端点

#### `POST /execute_plan`

**描述**:
接收计划状态，执行相应的计划步骤。

**请求参数**:
- `rewoo_state` (object): 包含计划状态的JSON对象。

**请求示例**:
```bash
curl -X POST "http://127.0.0.1:8000/execute_plan" \
-H "Content-Type: application/json" \
-d '{"rewoo_state": {"task": "任务：搜索最近热映电影","plan_string": "Plan: 使用WeekTop10工具获取当前热门电影列表。\n#E1 = WeekTop10[movies]","steps": [["使用WeekTop10工具获取当前热门电影列表。","#E1","WeekTop10","movies"]],"api_recommendations": {"nodes": [{"id": "fan_favorites","name": "FanFavorites","label": "FanFavorites","input": "query","description": "获取IMDb上的粉丝喜爱电影或系列。","type": "entertainment"},{"id": "search_imdb","name": "SearchIMDB","label": "SearchIMDB","input": "search query","description": "在IMDb上搜索信息。","type": "entertainment"}],"edges": []}}}'
```

**响应示例**:
```json
{
    "response": "API调用结果:\n以下是本周热门电影列表：\n1. The Boys - 评分：8.7\n2. House of the Dragon - 评分：8.4\n..."
}
```

**错误响应**:
- `400 Bad Request`:
  ```json
  {
      "detail": "No valid plan provided"
  }
  ```