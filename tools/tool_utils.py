import re
from tool_utils import *
import json


def get_location_id(input: str):
    input = input.replace("'", '"')
    try:
        location = json.loads(input)["id"]
    except Exception as e:
        location = "101010100"
        print(f"Location search failed, using default location. Error: {e}")
    return location
