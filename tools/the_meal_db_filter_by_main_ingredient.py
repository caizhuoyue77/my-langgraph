import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class FilterByMainIngredientInput(BaseModel):
    ingredient: str = Field(description="用于在TheMealDB数据库中过滤的主要成分。")

def process_filter_results(filter_results):
    important_fields = ['strMeal', 'strMealThumb', 'idMeal']
    parsed_data = {
        'meals': []
    }

    for meal in filter_results['meals'][:5]:
        parsed_meal = {key: meal[key] for key in important_fields if key in meal}
        parsed_data['meals'].append(parsed_meal)
    
    return parsed_data

async def filter_by_main_ingredient_iter(ingredient: str) -> dict:
    """
    Asynchronously filters TheMealDB using a specified main ingredient via the RapidAPI service.
    
    Args:
        ingredient (str): The main ingredient to filter by.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://themealdb.p.rapidapi.com/filter.php"
    querystring = {"i": ingredient}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "themealdb.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_filter_results(response.json())
        else:
            return {"error": f"Failed to filter by main ingredient, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def filter_by_main_ingredient(ingredient: str) -> dict:
    """
    A synchronous wrapper function to filter TheMealDB by main ingredient.

    Args:
        ingredient (str): The main ingredient to filter by.

    Returns:
        dict: The result from the asynchronous filter function, containing either the filter results or an error message.
    """
    return asyncio.run(filter_by_main_ingredient_iter(ingredient))

if __name__ == "__main__":
    main_ingredient = "egg"  # Replace 'egg' with your actual main ingredient
    ingredient_filter_results = filter_by_main_ingredient(main_ingredient)
    print("Filter Results:", ingredient_filter_results)
