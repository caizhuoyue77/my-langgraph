import re

regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*\[([^\]]+)\]"

# regex_pattern = r"Plan:\s*(.+)\s*(#E\d+)\s*=\s*(\w+)\s*(?:\[(.*?)\])?"



def get_plan():
    """生成任务计划。"""
    
    result = "Plan: 使用WeekTop10工具来获取当前一周的顶级电影或电视剧列表。\n#E1 = WeekTop10[input]"

    matches = re.findall(regex_pattern, result)
    
    print("计划步骤:")
    print(f"steps:{matches}")

get_plan()