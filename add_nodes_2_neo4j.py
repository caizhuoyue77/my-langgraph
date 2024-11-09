import json
import uuid
from neo4j import GraphDatabase

# Neo4j数据库连接配置
NEO4J_URI = "bolt://localhost:7687"  # 默认的Bolt连接地址
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "daffodil"

# 创建Neo4j驱动
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_api_node(api_name, tool_name, category_name):
    """在Neo4j中创建API、工具和类别节点，并建立关系
    :param api_name: API的全名
    :param tool_name: 工具名称
    :param category_name: 类别名称
    """
    api_id = str(uuid.uuid4())  # 生成API节点的UUID
    tool_id = str(uuid.uuid4())  # 生成工具节点的UUID
    category_id = str(uuid.uuid4())  # 生成类别节点的UUID

    with driver.session() as session:
        # 检查API是否已存在
        existing_api = session.run(
            "MATCH (a:API {name: $name}) RETURN a",
            name=api_name
        ).single()
        
        if not existing_api:
            # 创建API节点
            session.run(
                "CREATE (a:API {id: $id, name: $name})",
                id=api_id,
                name=api_name
            )
            print(f"创建API节点: {api_name}，ID: {api_id}")
        
        # 检查工具是否已存在
        existing_tool = session.run(
            "MATCH (t:Tool {name: $name}) RETURN t",
            name=tool_name
        ).single()
        
        if not existing_tool:
            # 创建工具节点
            session.run(
                "CREATE (t:Tool {id: $id, name: $name})",
                id=tool_id,
                name=tool_name
            )
            print(f"创建工具节点: {tool_name}，ID: {tool_id}")
        
        # 检查类别是否已存在
        existing_category = session.run(
            "MATCH (c:Category {name: $name}) RETURN c",
            name=category_name
        ).single()
        
        if not existing_category:
            # 创建类别节点
            session.run(
                "CREATE (c:Category {id: $id, name: $name})",
                id=category_id,
                name=category_name
            )
            print(f"创建类别节点: {category_name}，ID: {category_id}")

        # 建立API与工具的关系
        session.run(
            "MATCH (a:API {name: $api_name}), (t:Tool {name: $tool_name}) "
            "CREATE (a)-[:BELONGS_TO]->(t)",
            api_name=api_name,
            tool_name=tool_name
        )
        
        # 建立工具与类别的关系
        session.run(
            "MATCH (t:Tool {name: $tool_name}), (c:Category {name: $category_name}) "
            "CREATE (t)-[:BELONGS_TO]->(c)",
            tool_name=tool_name,
            category_name=category_name
        )

# 读取新的JSON文件
with open("rapidapi_all_apis_fullname.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# 遍历每个API对象
for obj in data:
    full_name = obj.get("full_name")
    tool_name = obj.get("tool_name")
    category_name = obj.get("category")

    if full_name and tool_name and category_name:  # 确保各个名称存在
        create_api_node(full_name, tool_name, category_name)

# 关闭Neo4j驱动
driver.close()