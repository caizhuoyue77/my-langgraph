import json
import os
from logger import *

CACHE_FILE = "cache.json"


def read_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def write_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False)


def convert_key_to_tuple(key):
    # Convert key to tuple if it's not already hashable
    if isinstance(key, list):
        return tuple(key)
    return key


def search_cache(query):
    cache = read_cache()
    key = convert_key_to_tuple(query)
    if key in cache:
        logger.debug("Cache命中")
        return cache[key]
    else:
        return None


def add_to_cache(query, result):
    cache = read_cache()
    key = convert_key_to_tuple(query)
    cache[key] = result
    write_cache(cache)
