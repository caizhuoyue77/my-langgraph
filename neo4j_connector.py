"""
Neo4jConnector类用于与Neo4j数据库进行交互，提供搜索节点邻居和计算边权重的功能。
"""

import json
from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri, user, password):
        """初始化Neo4j连接
        :param uri: Neo4j连接URI
        :param user: Neo4j用户名
        :param password: Neo4j密码
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """关闭Neo4j驱动"""
        self.driver.close()

    def find_neighbors(self, node_name: str) -> dict:
        """根据节点名称搜索其所有邻居及“call”边的数量
        :param node_name: 节点名称
        :return: 包含邻居节点及其与当前节点之间“call”边数量的字典
        """
        with self.driver.session() as session:
            try:
                # 执行查询，获取邻居节点及与当前节点之间的“call”边数量
                result = session.run(
                    """
                    MATCH (n {name: $name})-[:CALLS]->(m)
                    RETURN m.name AS neighbor, COUNT(*) AS call_count
                    """,
                    name=node_name
                )
                # 将结果转换为字典
                neighbors_info = {record["neighbor"]: record["call_count"] for record in result}
                return neighbors_info
            except Exception as exc:
                print(f"搜索邻居节点时发生错误: {exc}")
                return {}

    def calculate_edge_weight(self, from_node: str, to_node: str) -> float:
        """计算从一个节点到另一个节点的边的权重
        :param from_node: 起始节点名称
        :param to_node: 目标节点名称
        :return: 边的权重
        """
        with self.driver.session() as session:
            try:
                result = session.run(
                    "MATCH (n {name: $from_name})-[r]->(m {name: $to_name}) "
                    "RETURN r.weight AS weight",
                    from_name=from_node,
                    to_name=to_node
                )
                weight = result.single()
                return weight["weight"] if weight and "weight" in weight else None
            except Exception as exc:
                print(f"计算边权重时发生错误: {exc}")
                return None

    def get_all_api_nodes(self) -> list:
        """获取所有类型为API的节点名称
        :return: API节点名称的列表
        """
        with self.driver.session() as session:
            try:
                result = session.run(
                    "MATCH (n:API) RETURN n.name AS api_name"
                )
                return [record["api_name"] for record in result]
            except Exception as exc:
                print(f"获取API节点时发生错误: {exc}")
                return []

# 使用示例
if __name__ == "__main__":
    neo4j_uri = "bolt://localhost:7687"
    neo4j_user = "neo4j"
    neo4j_password = "daffodil"

    connector = Neo4jConnector(neo4j_uri, neo4j_user, neo4j_password)

    # 根据节点名称查找邻居及“call”边数量
    neighbors = connector.find_neighbors("trending_gifs_for_giphy")
    print(f"邻居节点及‘call’边数量: {neighbors}")

    # 获取所有API节点
    api_nodes = connector.get_all_api_nodes()
    print(f"所有API节点: {api_nodes}")

    # 计算边的权重示例
    # weight = connector.calculate_edge_weight("起始节点名称", "目标节点名称")
    # print(f"边的权重: {weight}")

    connector.close()