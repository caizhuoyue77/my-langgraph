import json
import os
from logger import *

CACHE_FILE = "cache.json"


def read_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def write_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def convert_key_to_str(key):
    # 将键转换为字符串，确保兼容性
    return str(key)


def search_cache(query):
    cache = read_cache()
    key = convert_key_to_str(query)
    if key in cache:
        logger.debug("Cache命中")
        return cache[key]
    else:
        return None


def add_to_cache(query, result):
    cache = read_cache()
    key = convert_key_to_str(query)
    cache[key] = result
    write_cache(cache)
