import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class LinkedInSearchJobsInput(BaseModel):
    geo_code: str = Field(description="地理位置代码。")
    date_posted: str = Field(default="any_time", description="职位发布的时间范围。")
    function_id: str = Field(description="职位的功能ID，多个功能用逗号分隔。")
    industry_code: str = Field(description="行业代码，多个行业用逗号分隔。")
    sort_by: str = Field(default="most_relevant", description="职位排序方式。")
    start: int = Field(default=0, description="搜索结果的起始位置。")
    easy_apply: bool = Field(default=False, description="是否只显示易于申请的职位。")
    under_10_applicants: bool = Field(default=False, description="是否只显示少于10个申请者的职位。")

def process_jobs_results(jobs_results):
    return jobs_results  # Customize this function based on the expected structure of the jobs results.

async def linkedin_search_jobs_iter(geo_code: str, function_id: str, industry_code: str, date_posted: str, sort_by: str, start: int, easy_apply: bool, under_10_applicants: bool) -> dict:
    """
    Asynchronously searches for jobs on LinkedIn using specified parameters via the RapidAPI service.
    
    Args:
        geo_code (str): The geographical code for the job location.
        function_id (str): The function IDs for the jobs, separated by commas.
        industry_code (str): The industry codes for the jobs, separated by commas.
        date_posted (str): The time range for the job posting.
        sort_by (str): The sorting method for the job results.
        start (int): The starting position for the search results.
        easy_apply (bool): Whether to show only easy apply jobs.
        under_10_applicants (bool): Whether to show only jobs with under 10 applicants.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://fresh-linkedin-profile-data.p.rapidapi.com/search-jobs"
    querystring = {
        "geo_code": geo_code,
        "function_id": function_id,
        "industry_code": industry_code,
        "date_posted": date_posted,
        "sort_by": sort_by,
        "start": start,
        "easy_apply": easy_apply,
        "under_10_applicants": under_10_applicants
    }
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "fresh-linkedin-profile-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_jobs_results(response.json())
        else:
            return {"error": f"Failed to search jobs on LinkedIn, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def linkedin_search_jobs(geo_code: str, function_id: str, industry_code: str, date_posted: str = "any_time", sort_by: str = "most_relevant", start: int = 0, easy_apply: bool = False, under_10_applicants: bool = False) -> dict:
    """
    A synchronous wrapper function to search for jobs on LinkedIn.

    Args:
        geo_code (str): The geographical code for the job location.
        function_id (str): The function IDs for the jobs, separated by commas.
        industry_code (str): The industry codes for the jobs, separated by commas.
        date_posted (str): The time range for the job posting.
        sort_by (str): The sorting method for the job results.
        start (int): The starting position for the search results.
        easy_apply (bool): Whether to show only easy apply jobs.
        under_10_applicants (bool): Whether to show only jobs with under 10 applicants.

    Returns:
        dict: The result from the asynchronous job search function, containing either the job results or an error message.
    """
    return asyncio.run(linkedin_search_jobs_iter(geo_code, function_id, industry_code, date_posted, sort_by, start, easy_apply, under_10_applicants))

if __name__ == "__main__":
    job_geo_code = "103644278"  # Replace with your actual geographical code
    job_function_id = "it,sale"  # Replace with your actual function IDs
    job_industry_code = "4,5"  # Replace with your actual industry codes
    linkedin_job_results = linkedin_search_jobs(
        geo_code=job_geo_code,
        function_id=job_function_id,
        industry_code=job_industry_code,
        date_posted="any_time",
        sort_by="most_relevant",
        start=0,
        easy_apply=False,
        under_10_applicants=False
    )
    print("LinkedIn Job Search Results:", linkedin_job_results)
