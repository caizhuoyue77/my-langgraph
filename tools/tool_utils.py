import re
from tool_utils import *
def get_location_id(input:str):
    if re.match(r'^\d+$', input.strip()):
        location = input
    else:
        try:
            location_result = search_location(input)
            location = location_result['location'][0]['id']
        except Exception as e:
            location = '101010100'
            print(f"Location search failed, using default location. Error: {e}")
    return location