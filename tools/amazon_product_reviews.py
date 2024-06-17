import asyncio
import requests
from pydantic import BaseModel, Field
from api_key_config import *

class AmazonProductReviewsInput(BaseModel):
    asin: str = Field(description="用于获取Amazon产品评论的ASIN码。")
    country: str = Field(default="US", description="用于搜索的国家代码。")
    sort_by: str = Field(default="TOP_REVIEWS", description="评论的排序方式。")
    star_rating: str = Field(default="ALL", description="筛选评论的星级。")
    verified_purchases_only: bool = Field(default=False, description="是否只显示经过验证的购买评论。")
    images_or_videos_only: bool = Field(default=False, description="是否只显示包含图片或视频的评论。")
    current_format_only: bool = Field(default=False, description="是否只显示当前格式的评论。")
    page: int = Field(default=1, description="搜索结果的页码。")

def process_reviews_results(reviews_results):
    important_fields = ['review_title', 'review_comment', 'review_star_rating', 'review_link']
    parsed_data = {
        'status': reviews_results['status'],
        'request_id': reviews_results['request_id'],
        'data': {
            'asin': reviews_results['data']['asin'],
            'total_reviews': reviews_results['data']['total_reviews'],
            'total_ratings': reviews_results['data']['total_ratings'],
            'country': reviews_results['data']['country'],
            'domain': reviews_results['data']['domain'],
            'reviews': []
        }
    }

    for review in reviews_results['data']['reviews'][:5]:
        parsed_review = {key: review[key] for key in important_fields}
        if len(parsed_review['review_comment']) > 100:
            parsed_review['review_comment'] = parsed_review['review_comment'][:100] + '...'
        parsed_data['data']['reviews'].append(parsed_review)

    return parsed_data

async def amazon_product_reviews_iter(asin: str, country: str, sort_by: str, star_rating: str, verified_purchases_only: bool, images_or_videos_only: bool, current_format_only: bool, page: int) -> dict:
    """
    Asynchronously retrieves Amazon product reviews using specified parameters via the RapidAPI service.
    
    Args:
        asin (str): The ASIN code for the product.
        country (str): The country code for the search.
        sort_by (str): The sorting method for the reviews.
        star_rating (str): The star rating to filter reviews.
        verified_purchases_only (bool): Whether to show only verified purchases reviews.
        images_or_videos_only (bool): Whether to show only reviews with images or videos.
        current_format_only (bool): Whether to show only reviews for the current format.
        page (int): The page number of reviews results.

    Returns:
        dict: A dictionary containing either the response JSON data or an error message.
    """
    url = "https://real-time-amazon-data.p.rapidapi.com/product-reviews"
    querystring = {
        "asin": asin,
        "country": country,
        "sort_by": sort_by,
        "star_rating": star_rating,
        "verified_purchases_only": verified_purchases_only,
        "images_or_videos_only": images_or_videos_only,
        "current_format_only": current_format_only,
        "page": page
    }
    headers = {
        'x-rapidapi-key': api_keys[0],
        'x-rapidapi-host': "real-time-amazon-data.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            return process_reviews_results(response.json())
        else:
            return {"error": f"Failed to retrieve Amazon product reviews, status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def amazon_product_reviews(asin: str, country: str = "US", sort_by: str = "TOP_REVIEWS", star_rating: str = "ALL", verified_purchases_only: bool = False, images_or_videos_only: bool = False, current_format_only: bool = False, page: int = 1) -> dict:
    """
    A synchronous wrapper function to retrieve Amazon product reviews.

    Args:
        asin (str): The ASIN code for the product.
        country (str): The country code for the search.
        sort_by (str): The sorting method for the reviews.
        star_rating (str): The star rating to filter reviews.
        verified_purchases_only (bool): Whether to show only verified purchases reviews.
        images_or_videos_only (bool): Whether to show only reviews with images or videos.
        current_format_only (bool): Whether to show only reviews for the current format.
        page (int): The page number of reviews results.

    Returns:
        dict: The result from the asynchronous reviews function, containing either the reviews results or an error message.
    """
    return asyncio.run(amazon_product_reviews_iter(asin, country, sort_by, star_rating, verified_purchases_only, images_or_videos_only, current_format_only, page))

if __name__ == "__main__":
    product_asin = "B09TMN58KL"  # Replace with your actual ASIN
    amazon_reviews_results = amazon_product_reviews(
        asin=product_asin,
    )
    print("Product Reviews Results:", amazon_reviews_results)
