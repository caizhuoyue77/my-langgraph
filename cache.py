import json
import os
from logger import *

CACHE_FILE = 'cache.json'

def read_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def write_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False)

def search_cache(query):
    cache = read_cache()
    if query in cache:
        logger.debug("Cache命中")
        return cache[query]
    else:
        return None
    
def add_to_cache(query, result):
    cache = read_cache()
    cache[query] = result
    write_cache(cache)