# Copyright (c) 2024 Microsoft Corporation.
# Licensed under the MIT License

"""A module containing 'GraphExtractionResult' and 'GraphExtractor' models."""

import logging
import re
import traceback
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, List, Dict
from free_gpt import get_chat_response, count_tokens
import os
import json
import random
import csv

import networkx as nx
import tiktoken
from prompts import CONTINUE_PROMPT, GRAPH_EXTRACTION_PROMPT, LOOP_PROMPT

DEFAULT_TUPLE_DELIMITER = "<|>"
DEFAULT_RECORD_DELIMITER = "##"
DEFAULT_COMPLETION_DELIMITER = "<|COMPLETE|>"
# DEFAULT_ENTITY_TYPES = ["organization", "person", "geo", "event", "location", "time", "date", "other"]
DEFAULT_ENTITY_TYPES = ["API", "tool", "parameter", "type", "organization", "other"]
DEFAULT_ENTITY_STR = ','.join(DEFAULT_ENTITY_TYPES)


async def _process_results(
    self,
    results: dict[int, str],
    tuple_delimiter: str,
    record_delimiter: str,
) -> nx.Graph:
    """Parse the result string to create an undirected unipartite graph.

    Args:
        - results - dict of results from the extraction chain
        - tuple_delimiter - delimiter between tuples in an output record, default is '<|>'
        - record_delimiter - delimiter between records, default is '##'
    Returns:
        - output - unipartite graph in graphML format
    """
    graph = nx.Graph()
    for source_doc_id, extracted_data in results.items():
        records = [r.strip() for r in extracted_data.split(record_delimiter)]

        for record in records:
            record = re.sub(r"^\(|\)$", "", record.strip())
            record_attributes = record.split(tuple_delimiter)

            if record_attributes[0] == '"entity"' and len(record_attributes) >= 4:
                # add this record as a node in the G
                entity_name = clean_str(record_attributes[1].upper())
                entity_type = clean_str(record_attributes[2].upper())
                entity_description = clean_str(record_attributes[3])

                if entity_name in graph.nodes():
                    node = graph.nodes[entity_name]
                    if self._join_descriptions:
                        node["description"] = "\n".join(
                            list({
                                *_unpack_descriptions(node),
                                entity_description,
                            })
                        )
                    else:
                        if len(entity_description) > len(node["description"]):
                            node["description"] = entity_description
                    node["source_id"] = ", ".join(
                        list({
                            *_unpack_source_ids(node),
                            str(source_doc_id),
                        })
                    )
                    node["entity_type"] = (
                        entity_type if entity_type != "" else node["entity_type"]
                    )
                else:
                    graph.add_node(
                        entity_name,
                        type=entity_type,
                        description=entity_description,
                        source_id=str(source_doc_id),
                    )

            if (
                record_attributes[0] == '"relationship"'
                and len(record_attributes) >= 5
            ):
                # add this record as edge
                source = clean_str(record_attributes[1].upper())
                target = clean_str(record_attributes[2].upper())
                edge_description = clean_str(record_attributes[3])
                edge_source_id = clean_str(str(source_doc_id))
                try:
                    weight = float(record_attributes[-1])
                except ValueError:
                    weight = 1.0

                if source not in graph.nodes():
                    graph.add_node(
                        source,
                        type="",
                        description="",
                        source_id=edge_source_id,
                    )
                if target not in graph.nodes():
                    graph.add_node(
                        target,
                        type="",
                        description="",
                        source_id=edge_source_id,
                    )
                if graph.has_edge(source, target):
                    edge_data = graph.get_edge_data(source, target)
                    if edge_data is not None:
                        weight += edge_data["weight"]
                        if self._join_descriptions:
                            edge_description = "\n".join(
                                list({
                                    *_unpack_descriptions(edge_data),
                                    edge_description,
                                })
                            )
                        edge_source_id = ", ".join(
                            list({
                                *_unpack_source_ids(edge_data),
                                str(source_doc_id),
                            })
                        )
                graph.add_edge(
                    source,
                    target,
                    weight=weight,
                    description=edge_description,
                    source_id=edge_source_id,
                )

    return graph


    
def my_extraction(input_text:str = "韩国连续三天暴雨不断，强降雨破坏了房屋、道路和基础设施，1500多人被迫撤离。《韩国先驱报》报道，强降雨从9月19日下午持续到9月21日，先在济州岛开始，然后扩大到韩国全境。"):
    # 1. get the graph
    prompt = GRAPH_EXTRACTION_PROMPT
    
    prompt = prompt.replace('{tuple_delimiter}', DEFAULT_TUPLE_DELIMITER)
    prompt = prompt.replace('{record_delimiter}', DEFAULT_RECORD_DELIMITER)
    prompt = prompt.replace('{entity_types}', DEFAULT_ENTITY_STR)
    prompt = prompt.replace('{completion_delimiter}', DEFAULT_COMPLETION_DELIMITER)
    prompt = prompt.replace('{input_text}', input_text)

    result = get_chat_response(prompt)
    
    return result
 

def parse_graph_data(data: str) -> nx.Graph:
    """解析图数据字符串并返回无向图对象。

    参数:
    data (str): 包含图数据的字符串，使用特定的分隔符分隔。

    返回:
    nx.Graph: 解析后的无向图。
    """
    graph = {}
    nodes = []
    edges = []
    
    # graph = nx.Graph()
    records = [record.strip() for record in data.split("##")]

    for record in records:
        record = re.sub(r"^\(|\)$", "", record.strip())
        record_attributes = record.split("<|>")

        if record_attributes[0] == '"entity"' and len(record_attributes) >= 4:
            entity_name = record_attributes[1].strip('"').upper()
            entity_type = record_attributes[2].strip('"').upper()
            entity_description = record_attributes[3].strip('"')
            
            nodes.append({"name": entity_name, "type": entity_type, "description": entity_description})

            # graph.add_node(
            #     entity_name,
            #     type=entity_type,
            #     description=entity_description,
            # )

        if record_attributes[0] == '"relationship"' and len(record_attributes) >= 5:
            source = record_attributes[1].strip('"').upper()
            target = record_attributes[2].strip('"').upper()
            edge_description = record_attributes[3].strip('"')
            weight = float(record_attributes[4]) if record_attributes[4].isdigit() else 1.0
            
            edges.append({"source": source, "target": target, "weight": weight, "description": edge_description})

            # graph.add_edge(
            #     source,
            #     target,
            #     weight=weight,
            #     description=edge_description,
            # )

    return nodes, edges

def write_jsonl_output(directory: str, output_file: str) -> None:
    """
    遍历指定目录及其所有子目录中的 JSON 文件，每个子文件夹随机选择 10 个 JSON 文件，
    并将其信息以 JSON Lines 格式写入到指定的输出文件中。
    
    参数:
    directory (str): JSON 文件所在的根目录路径
    output_file (str): 输出的 JSON Lines 文件路径
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # 使用 os.walk() 遍历根目录及其所有子目录
            for root, dirs, files in os.walk(directory):
                # 只处理 .json 结尾的文件
                json_files = [file for file in files if file.endswith('.json')]
                
                # 如果 json 文件数量大于 10，随机选择 10 个文件
                if len(json_files) > 10:
                    selected_files = random.sample(json_files, 10)
                else:
                    selected_files = json_files

                # 处理每个被选中的 JSON 文件
                for json_file in selected_files:
                    json_path = os.path.join(root, json_file)
                    
                    try:
                        with open(json_path, 'r', encoding='utf-8') as file:
                            content = json.load(file)

                            # 提取字段
                            folder_name = os.path.basename(root)
                            file_path = json_path
                            tool_name = content.get('name', '')
                            description = content.get('tool_description', '')

                            # 写入 JSON Lines 格式
                            json_line = {
                                'folder_name': folder_name,
                                'file_path': file_path,
                                'tool_name': tool_name,
                                'description': description
                            }
                            outfile.write(json.dumps(json_line, ensure_ascii=False) + '\n')
                    
                    except json.JSONDecodeError as json_error:
                        print(f"文件解析失败: {json_file}, 错误: {json_error}")
                    except FileNotFoundError as fnf_error:
                        print(f"文件未找到: {fnf_error}")
                    except Exception as e:
                        print(f"处理文件 {json_file} 时出错: {e}")

    except FileNotFoundError as fnf_error:
        print(f"目录未找到: {fnf_error}")
    except PermissionError as perm_error:
        print(f"权限不足: {perm_error}")
    except Exception as e:
        print(f"出现错误: {e}")

def load_json_from_jsonl(jsonl_file: str) -> List[Dict]:
    """
    读取 JSON Lines 文件，根据每个记录中的 'file_path' 字段读取对应的 JSON 文件，
    并返回所有 JSON 文件的内容对象列表。
    
    参数:
    jsonl_file (str): 包含 JSON 对象的 JSON Lines 文件路径
    
    返回:
    List[Dict]: 包含所有 JSON 文件内容对象的列表
    """
    json_objects = []

    try:
        with open(jsonl_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                record = json.loads(line)
                file_path = record.get('file_path', '')
                
                if file_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as json_file:
                            content = json.load(json_file)
                            json_objects.append(content)
                    
                    except json.JSONDecodeError as json_error:
                        print(f"文件解析失败: {file_path}, 错误: {json_error}")
                    except FileNotFoundError as fnf_error:
                        print(f"文件未找到: {fnf_error}")
                    except Exception as e:
                        print(f"处理文件 {file_path} 时出错: {e}")

    except FileNotFoundError as fnf_error:
        print(f"文件未找到: {fnf_error}")
    except PermissionError as perm_error:
        print(f"权限不足: {perm_error}")
    except Exception as e:
        print(f"出现错误: {e}")

    return json_objects


def append_to_csv(file_path: str, data: list, fieldnames: list):
    """将数据追加到 CSV 文件中"""
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # 如果文件不存在，则写入表头
        writer.writerows(data)

if __name__ == '__main__':
    # 你要遍历的文件夹路径
    directory_path = "/Users/caizhuoyue/Desktop/my-langgraph/data/RapidAPIHub-sample/tools"
    # 输出的 JSON Lines 文件路径
    output_file_path = "/Users/caizhuoyue/Desktop/my-langgraph/data/RapidAPIHub-sample/output.jsonl"

    # 调用函数，随机选择每个子文件夹中的 10 个 JSON 文件，并输出到 JSON Lines 文件
    write_jsonl_output(directory_path, output_file_path)

    # 根据 JSON Lines 文件读取所有 JSON 文件的内容
    json_objects = load_json_from_jsonl(output_file_path)
    
    json_objects = json_objects[:3]
    
    graph = {"nodes": [], "edges": []}
    
    idx = 0
    
    for json_object in json_objects:
        temp = {}
        temp["tool_name"] = json_object["tool_name"]
        temp["tool_description"] = json_object["tool_description"]
        temp["api_list"] = []
        
        for api in json_object["api_list"]:
            temp["api_list"].append({"name": api["name"], "description": api["description"], "method": api["method"]})
        
        print(temp)
        
        print(f"idx:{idx}")
        idx += 1
        
        input_text = str(temp)
        
        if(count_tokens(input_text) > 2000):
            input_text = input_text[:2000]

        data = my_extraction(input_text)
        nodes, edges = parse_graph_data(data)
        
        print(f"新nodes个数{len(nodes)}")
    
        graph["nodes"].extend(nodes)
        graph["edges"].extend(edges)
        
        append_to_csv(
            "/Users/caizhuoyue/Desktop/my-langgraph/data/RapidAPIHub-sample/nodes-923.csv", 
            nodes, 
            fieldnames=["name", "type", "description"]
        )
        
        append_to_csv(
            "/Users/caizhuoyue/Desktop/my-langgraph/data/RapidAPIHub-sample/edges-923.csv", 
            edges, 
            fieldnames=["source", "target", "weight", "description"]
        )
        
            
    print(graph)    