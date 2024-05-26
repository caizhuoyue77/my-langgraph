import asyncio
import requests
from pydantic import BaseModel, Field

class UpcomingMoviesInput(BaseModel):
    region: str = Field(default="CHN", description="The region for which to fetch upcoming movies.")


import json
from datetime import datetime


def filter_movies(nested_json_data):
    # 将嵌套JSON字符串解析为Python对象
    data = nested_json_data
    # data = json.loads(nested_json_data)

    # 检查数据结构是否正确
    if not data.get("message"):
        return json.dumps([], indent=4)
    
    # 处理电影信息并只保留所需的信息
    filtered_movies = []

    for group in data["message"]:
        for entry in group.get("entries", []):
            if len(filtered_movies) >= 20:
                break
            filtered_movie = {
                "title": entry.get("titleText"),
                "releaseDate": entry.get("releaseDate"),
                "genres": entry.get("genres"),
                "principalCredits": [credit.get("text") for credit in entry.get("principalCredits", [])]
            }
            filtered_movies.append(filtered_movie)

        if len(filtered_movies) >= 20:
            break

    # 格式化日期并返回处理后的信息
    for movie in filtered_movies:
        if movie["releaseDate"]:
            movie["releaseDate"] = datetime.strptime(movie["releaseDate"], "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d")
    
    return json.dumps(filtered_movies,ensure_ascii = False, indent=4)


async def fetch_upcoming_movies_iter(region: str) -> dict:
    """
    Asynchronously fetches a list of upcoming movies for a specified region from IMDb via the RapidAPI service.
    
    Args:
        region (str): The region code for which to fetch upcoming movies.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://imdb188.p.rapidapi.com/api/v1/getUpcomingMovies"
    querystring = {"region": region}
    headers = {
        "X-RapidAPI-Key": "e873f2422cmsh92c1c839d99aee8p1dfd77jsne5cf72c01848",
        "X-RapidAPI-Host": "imdb188.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return filter_movies(response.json())
        else:
            return {"error": f"Failed to fetch upcoming movies for region {region}, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def upcoming_movies(region: str = "CHN") -> dict:
    """
    A synchronous wrapper function to fetch a list of upcoming movies for a specified region from IMDb.

    Args:
        region (str): The region code, defaults to 'US'.

    Returns:
        dict: The result from the asynchronous fetch function, containing either the upcoming movies list or an error message.
    """
    return asyncio.run(fetch_upcoming_movies_iter(region))

if __name__ == "__main__":
    upcoming_movies_data = upcoming_movies()
    print("Upcoming Movies:", upcoming_movies_data)
