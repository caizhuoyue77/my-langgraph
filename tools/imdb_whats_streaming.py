import asyncio
import requests
from pydantic import BaseModel, Field

class WhatsStreamingInput(BaseModel):
    country: str = Field(default="US", description="国家代码，用于查询该国的流媒体内容。")

async def fetch_whats_streaming_iter(country: str) -> dict:
    """
    Asynchronously fetches information on what's currently streaming in a specified country from IMDb via the RapidAPI service.
    
    Args:
        country (str): The country code for which to fetch streaming information.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb188.p.rapidapi.com/api/v1/getWhatsStreaming"
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
            return {"error": f"Failed to fetch streaming information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def fetch_whats_streaming(country: str = "US") -> dict:
    """
    A synchronous wrapper function to fetch information on what's currently streaming in a specified country from IMDb.

    Args:
        country (str): The country code, defaults to 'US'.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the streaming information or an error message.
    """
    country = "US"
    return asyncio.run(fetch_whats_streaming_iter(country))

if __name__ == "__main__":
    streaming_data = fetch_whats_streaming()
    print("What's Streaming:", streaming_data)
