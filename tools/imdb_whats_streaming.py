import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *
import json

def process_whats_streaming(data):
    important_fields = []

    for item in data['data'][:2]:
        print(item)
        print("")
        print("")
        # title_info = item["title"]
        # primary_image = title_info["primaryImage"]
        # ratings_summary = title_info["ratingsSummary"]

        # extracted_info = {
        #     'id': title_info["id"],
        #     'title': title_info["titleText"]["text"],
        #     'originalTitle': title_info["originalTitleText"]["text"],
        #     'year': title_info["releaseYear"]["year"],
        #     'rating': ratings_summary["aggregateRating"],
        #     'voteCount': ratings_summary["voteCount"],
        #     'imageUrl': primary_image["imageUrl"],
        #     'isAdult': title_info["isAdult"],
        #     'isSeries': title_info["isSeries"],
        #     'isEpisode': title_info["isEpisode"]
        # }

        # important_fields.append(extracted_info)

    return important_fields

class WhatsStreamingInput(BaseModel):
    country: str = Field(default="CHN", description="国家代码，用于查询该国的流媒体内容。")

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
        "X-RapidAPI-Key": api_keys[0],
        "X-RapidAPI-Host": "imdb188.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_whats_streaming(response.json())
        else:
            return {"error": f"Failed to fetch streaming information, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def whats_streaming(country: str = "CHN") -> dict:
    """
    A synchronous wrapper function to fetch information on what's currently streaming in a specified country from IMDb.

    Args:
        country (str): The country code, defaults to 'US'.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the streaming information or an error message.
    """
    return asyncio.run(fetch_whats_streaming_iter(country))

if __name__ == "__main__":
    streaming_data = whats_streaming()
    # print("What's Streaming:", json.dumps(streaming_data, indent=4))
