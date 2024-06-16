import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import api_keys

class FilterByMultiIngredientInput(BaseModel):
    ingredients: str = Field(description="用于在TheMealDB数据库中过滤的多种成分，多个成分用逗号分隔。")

def process_filter_results(filter_results):
    important_fields = ['strMeal', 'strMealThumb', 'idMeal']
    parsed_data = {
        'meals': []
    }

    meals = filter_results.get('meals')
    if meals:
        for meal in meals[:5]:
            parsed_meal = {key: meal.get(key, "") for key in important_fields}
            parsed_data['meals'].append(parsed_meal)
    else:
        parsed_data['meals'] = "没有搜索结果"

    return parsed_data

async def filter_by_multi_ingredient_iter(ingredients: str) -> dict:
    """
    Asynchronously filters TheMealDB using specified multiple ingredients via the RapidAPI service.
    
    Args:
        ingredients (str): The ingredients to filter by, separated by commas.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://themealdb.p.rapidapi.com/filter.php"
    querystring = {"i": ingredients}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "themealdb.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_filter_results(response.json())
        else:
            return {"error": f"Failed to filter by multi-ingredients, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def filter_by_multi_ingredient(ingredients: str) -> dict:
    """
    A synchronous wrapper function to filter TheMealDB by multiple ingredients.

    Args:
        ingredients (str): The ingredients to filter by, separated by commas.

    Returns:
        dict: The result from the asynchronous filter function, containing either the filter results or an error message.
    """
    return asyncio.run(filter_by_multi_ingredient_iter(ingredients))

if __name__ == "__main__":
    multi_ingredients = "chicken,egg"  # Replace with your actual ingredients
    multi_ingredients_filter_results = filter_by_multi_ingredient(multi_ingredients)
    print("Filter Results:", multi_ingredients_filter_results)
