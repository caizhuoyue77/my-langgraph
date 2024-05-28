import json
import asyncio
from pydantic import BaseModel, Field
import requests
import re
from datetime import datetime, timedelta

def calc_datetime(date:str, days:int):
    date = datetime.strptime(date, "%Y-%m-%d")
    date += timedelta(days=days)
    return date.strftime("%Y-%m-%d")

def get_current_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")