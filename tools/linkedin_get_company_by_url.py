import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class LinkedInGetCompanyByUrlInput(BaseModel):
    linkedin_url: str = Field(description="用于获取LinkedIn公司资料的URL。")

def process_company_results(company_results):
    data = company_results.get('data', {})
    
    processed_data = {
        "company_name": data.get("company_name"),
        "description": data.get("description"),
        "domain": data.get("domain"),
        "employee_count": data.get("employee_count"),
        "employee_range": data.get("employee_range"),
        "industries": data.get("industries"),
        "linkedin_url": data.get("linkedin_url"),
        "website": data.get("website")
    }

    return processed_data

async def linkedin_get_company_by_url_iter(linkedin_url: str) -> dict:
    """
    Asynchronously retrieves a company profile from LinkedIn using specified parameters via the RapidAPI service.
    
    Args:
        linkedin_url (str): The URL of the LinkedIn company profile.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://fresh-linkedin-profile-data.p.rapidapi.com/get-company-by-linkedinurl"
    querystring = {"linkedin_url": linkedin_url}
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "fresh-linkedin-profile-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_company_results(response.json())
        else:
            return {"error": f"Failed to retrieve LinkedIn company profile, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def linkedin_get_company_by_url(linkedin_url: str) -> dict:
    """
    A synchronous wrapper function to retrieve a company profile from LinkedIn.

    Args:
        linkedin_url (str): The URL of the LinkedIn company profile.

    Returns:
        dict: The result from the asynchronous company profile function, containing either the company profile results or an error message.
    """
    return asyncio.run(linkedin_get_company_by_url_iter(linkedin_url))

if __name__ == "__main__":
    company_url = "https://www.linkedin.com/company/apple/"  # Replace with your actual company profile URL
    linkedin_company_results = linkedin_get_company_by_url(company_url)
    print("LinkedIn Company Profile Results:", linkedin_company_results)
