import asyncio
import requests
from pydantic import BaseModel, Field

class FanFavoritesInput(BaseModel):
    country: str = Field(default="US", description="国家代码，用于获取该国家的粉丝最喜爱的影视作品。")

async def fan_favorites_iter(country: str) -> dict:
    """
    Asynchronously fetches fan favorites from IMDb for a specified country via the RapidAPI service.
    
    Args:
        country (str): The country code to fetch fan favorites for.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb188.p.rapidapi.com/api/v1/getFanFavorites"
    querystring = {"country": country}
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "imdb188.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch fan favorites, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def fan_favorites(country: str = "US") -> dict:
    """
    A synchronous wrapper function to fetch fan favorites from IMDb for a specified country.

    Args:
        country (str): The country code, defaults to 'US'.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the fan favorites or an error message.
    """
    country="US"
    return asyncio.run(fan_favorites_iter(country))

if __name__ == "__main__":
    fan_favorites_data = fan_favorites()
    print("Fan Favorites:", fan_favorites_data)