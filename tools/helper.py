import re

def get_location_id(input:str)->str:
    pattern = r'location[^\d]*?(\d{9})'
    match = re.search(pattern, input)
    if match:
        location = match.group(1)
    else:
        location = "101010100"
    return location

def get_lon_lat(input:str)->str:
    pattern = ""
    return "116.38,39.91"

def get_date(input:str)->str:
    pattern = r'date[^\d]*?(\d{8})'
    match = re.search(pattern, input)
    if match:
        date = match.group(1)
    else:
        date = "20240530"
    return date