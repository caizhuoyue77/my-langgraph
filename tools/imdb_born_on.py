import asyncio
import requests
from pydantic import BaseModel, Field

class BornOnInput(BaseModel):
    month: str = Field(description="查询的月份，格式为两位数字（例如：'01'）。")
    day: str = Field(description="查询的日，格式为两位数字（例如：'01'）。")

async def fetch_born_on_iter(month: str, day: str) -> dict:
    """
    Asynchronously fetches a list of celebrities born on a specified date from IMDb via the RapidAPI service.
    
    Args:
        month (str): The month of the birthdate to query.
        day (str): The day of the birthdate to query.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb188.p.rapidapi.com/api/v1/getBornOn"
    querystring = {"month": month, "day": day}
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "imdb188.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch celebrities born on {month}-{day}, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def fetch_born_on(month: str, day: str) -> dict:
    """
    A synchronous wrapper function to fetch a list of celebrities born on a specified date from IMDb.

    Args:
        month (str): The month of the birthdate to query.
        day (str): The day of the birthdate to query.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the list of celebrities or an error message.
    """
    return asyncio.run(fetch_born_on_iter(month, day))

if __name__ == "__main__":
    born_on_data = fetch_born_on("01", "01")
    print("Celebrities Born On 01-01:", born_on_data)
