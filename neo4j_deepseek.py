from neo4j import GraphDatabase
import pandas as pd

# Neo4j 配置
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"  # 替换为你的用户名
NEO4J_PASSWORD = "daffodil"  # 替换为你的密码

# CSV 文件路径
CSV_FILE = "data/deepseek_edges_filtered.csv"

class Neo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        """清空数据库"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("数据库已清空。")

    def import_data(self, df):
        """导入 CSV 数据到 Neo4j"""
        with self.driver.session() as session:
            for _, row in df.iterrows():
                row_dict = row.to_dict()  # 转换为字典形式

                # 填充 NaN 值为空字符串，确保参数完整
                row_dict = {k: (v if pd.notnull(v) else "") for k, v in row_dict.items()}

                # 创建 Tool 和 API 节点
                session.run("""
                MERGE (tool1:Tool {name: $tool1_name})
                MERGE (tool2:Tool {name: $tool2_name})
                MERGE (api1:API {hash_id: $api1, name: $api1_name})
                MERGE (api2:API {hash_id: $api2, name: $api2_name})
                MERGE (api1)-[:BELONGS_TO]->(tool1)
                MERGE (api2)-[:BELONGS_TO]->(tool2)
                """, 
                tool1_name=row_dict['api_1_tool_name'],
                tool2_name=row_dict['api_2_tool_name'],
                api1=row_dict['api_1'],
                api1_name=row_dict['api_1_name'],
                api2=row_dict['api_2'],
                api2_name=row_dict['api_2_name'])

                # 创建 API 之间的依赖关系（如果有依赖参数）
                session.run("""
                MATCH (api1:API {hash_id: $api1})
                MATCH (api2:API {hash_id: $api2})
                MERGE (api1)-[:DEPENDS_ON {description: $description}]->(api2)
                """, 
                api1=row_dict['api_1'],
                api2=row_dict['api_2'],
                description=row_dict['dependency_description']
                )
            print("数据导入完成。")

# 主流程
if __name__ == "__main__":
    # 连接 Neo4j
    importer = Neo4jImporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    try:
        # 清空数据库
        importer.clear_database()

        # 加载 CSV 数据
        df = pd.read_csv(CSV_FILE)

        # 导入数据到 Neo4j
        importer.import_data(df)
    finally:
        importer.close()