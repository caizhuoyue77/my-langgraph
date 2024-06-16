
import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class LinkedInGetPersonalProfileInput(BaseModel):
    profile_url: str = Field(description="用于获取LinkedIn个人资料的URL。")

def process_profile_results(profile_results):
    return profile_results  # Customize this function based on the expected structure of the profile results.

async def linkedin_get_personal_profile_iter(profile_url: str) -> dict:
    """
    Asynchronously retrieves a personal profile from LinkedIn using specified parameters via the RapidAPI service.
    
    Args:
        profile_url (str): The URL of the LinkedIn profile.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://linkedin-data.p.rapidapi.com/linkedin_get_personal_profile"
    querystring = {"url": profile_url}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "linkedin-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_profile_results(response.json())
        else:
            return {"error": f"Failed to retrieve LinkedIn personal profile, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def linkedin_get_personal_profile(profile_url: str) -> dict:
    """
    A synchronous wrapper function to retrieve a personal profile from LinkedIn.

    Args:
        profile_url (str): The URL of the LinkedIn profile.

    Returns:
        dict: The result from the asynchronous profile function, containing either the profile results or an error message.
    """
    return asyncio.run(linkedin_get_personal_profile_iter(profile_url))

# 似乎就是不能用
if __name__ == "__main__":
    profile_url = "https://www.linkedin.com/in/%E5%8D%93%E6%82%A6-%E8%94%A1-965a1016b/"  # Replace with your actual profile URL
    linkedin_profile_results = linkedin_get_personal_profile(profile_url)
    print("LinkedIn Personal Profile Results:", linkedin_profile_results)
