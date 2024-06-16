import os
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config_api_keys import TAVILY_API_KEY, OPENAI_API_KEY
from langchain_community.tools.tavily_search import TavilySearchResults

import sys

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将tools目录添加到sys.path中
tools_dir = os.path.join(current_dir, 'tools')
sys.path.append(tools_dir)

from calc_datetime import calc_datetime, get_current_date, get_current_time
from bookings_get_currency import get_currency
from bookings_get_exchange_rates import get_exchange_rates
from bookings_get_languages import get_languages
from bookings_location_to_lat_lon import location_to_lat_lon
from bookings_search_flight_location import search_flight_location
from bookings_search_flights_min_price import search_flights_min_price
from bookings_search_flights import search_flights
from bookings_search_hotel_destination import search_hotel_destination
from bookings_search_hotels import search_hotels
from qweather_search_location import search_location
from qweather_sunrise_sunset import sunrise_sunset
from qweather_weather_forecast_3d import weather_forecast_3d
from qweather_weather_forecast_7d import weather_forecast_7d
from qweather_weather_forecast_24h import weather_forecast_24h
from qweather_weather_index_1d import weather_index_1d
from qweather_weather_rain_minute import weather_rain_minute
from imdb_born_on import born_on
from imdb_fan_favorites import fan_favorites
from imdb_search_imdb import search_imdb
from imdb_top_100_movies import top_100_movies
from imdb_top_100_series import top_100_series
from imdb_upcoming_movies import upcoming_movies
from imdb_week_top_10 import week_top_10
from imdb_whats_streaming import whats_streaming
from logger import *

# 导入新添加的工具API
from amazon_best_sellers import amazon_best_sellers
from amazon_product_by_category import amazon_product_by_category
from amazon_product_details import amazon_product_details
from amazon_product_reviews import amazon_product_reviews
from amazon_product_search import amazon_product_search
from google_news_business import google_news_business
from google_news_entertainment import google_news_entertainment
from google_news_latest import google_news_latest
from google_news_science import google_news_science
from google_news_search import google_news_search
# from google_news_sport import google_news_sport
from google_news_suggest import google_news_suggest
from google_news_technology import google_news_technology
from google_news_world import google_news_world
from linkedin_get_company_by_url import linkedin_get_company_by_url
from linkedin_get_personal_profile import linkedin_get_personal_profile
from linkedin_search_jobs import linkedin_search_jobs
from the_meal_db_filter_by_area import filter_by_area
from the_meal_db_filter_by_category import filter_by_category
from the_meal_db_filter_by_main_ingredient import filter_by_main_ingredient
from the_meal_db_filter_by_multi_ingredient import filter_by_multi_ingredient

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def use_actual_tool(tool: str, tool_input: dict):
    logger.info(f"调用工具：{tool}")
    logger.info(f"工具输入：{tool_input}")
    search = TavilySearchResults()

    # 通用API
    if tool == "Google":
        result = search.invoke(tool_input)
    # 天气API
    elif tool == "WeatherForecast24H":
        result = weather_forecast_24h(tool_input)
    elif tool == "SunriseSunset":
        result = sunrise_sunset(tool_input)
    elif tool == "WeatherForecast3D":
        result = weather_forecast_3d(tool_input)
    elif tool == "WeatherForecast7D":
        result = weather_forecast_7d(tool_input)
    elif tool == "WeatherIndex1D":
        result = weather_index_1d(tool_input)
    elif tool == "WeatherRainMinute":
        result = weather_rain_minute(tool_input)
    elif tool == "SearchLocation":
        result = search_location(tool_input)
    # 酒店API
    elif tool == "SearchHotelDestination":
        result = search_hotel_destination(tool_input)
    elif tool == "SearchHotels":
        result = search_hotels(tool_input)
    # 机票API
    elif tool == "SearchFlightLocation":
        result = search_flight_location(tool_input)
    elif tool == "SearchFlightsMinPrice":
        result = search_flights_min_price(tool_input)
    elif tool == "SearchFlights":
        result = search_flights(tool_input)
    # 货币/语言API
    elif tool == "GetCurrency":
        result = get_currency(tool_input)
    elif tool == "GetExchangeRates":
        result = get_exchange_rates(tool_input)
    elif tool == "LocationToLatLon":
        result = location_to_lat_lon(tool_input)
    # IMDb 电影/电视剧API
    elif tool == "FanFavorites":
        result = fan_favorites()
    elif tool == "SearchIMDB":
        result = search_imdb(tool_input)
    elif tool == "Top100Movies":
        result = top_100_movies()
    elif tool == "Top100Series":
        result = top_100_series()
    elif tool == "UpcomingMovies":
        result = upcoming_movies()
    elif tool == "WeekTop10":
        result = week_top_10()
    elif tool == "WhatsStreaming":
        result = whats_streaming()
    # 自己编写的API
    elif tool == "GetCurrentTime":
        result = get_current_time()
    elif tool == "GetCurrentDate":
        result = get_current_date()
    
    elif tool == "CalcDatetime":
        result = calc_datetime("20240620",20)
    # 新添加的API工具
    elif tool == "AmazonProductByCategory":
        # 要输入category_id
        result = amazon_product_by_category(tool_input)
    elif tool == "AmazonProductDetails":
        # 要输入产品asin
        result = amazon_product_details(tool_input)
    elif tool == "AmazonProductReviews":
        # 要输入产品asin
        result = amazon_product_reviews(tool_input)
    elif tool == "AmazonProductSearch":
        result = amazon_product_search(tool_input)
    # elif tool == "GoogleNewsBusiness":
    #     result = google_news_business(tool_input)
    # elif tool == "GoogleNewsEntertainment":
    #     result = google_news_entertainment(tool_input)
    # elif tool == "GoogleNewsLatest":
    #     result = google_news_latest(tool_input)
    # elif tool == "GoogleNewsScience":
    #     result = google_news_science(tool_input)
    # elif tool == "GoogleNewsSearch":
    #     result = google_news_search(tool_input)
    # elif tool == "GoogleNewsSport":
    #     result = google_news_sport(tool_input)
    # elif tool == "GoogleNewsSuggest":
    #     result = google_news_suggest(tool_input)
    # elif tool == "GoogleNewsTechnology":
    #     result = google_news_technology(tool_input)
    # elif tool == "GoogleNewsWorld":
    #     result = google_news_world(tool_input)
    # elif tool == "LinkedInGetCompanyByUrl":
    #     result = linkedin_get_company_by_url(tool_input)
    # elif tool == "LinkedInGetPersonalProfile":
    #     result = linkedin_get_personal_profile(tool_input)
    # elif tool == "LinkedInSearchJobs":
    #     result = linkedin_search_jobs(tool_input)
    elif tool == "FilterByArea":
        result = filter_by_area(tool_input)
    elif tool == "FilterByCategory":
        result = filter_by_category(tool_input)
    elif tool == "FilterByMainIngredient":
        result = filter_by_main_ingredient(tool_input)
    elif tool == "FilterByMultiIngredient":
        result = filter_by_multi_ingredient(tool_input)
    else:
        result = ""
        # raise ValueError(f"Unknown tool: {tool}")
    logger.critical("这是调用的结果呀:" + str(result))
    return result

def test_all_tools():
    tools = {
        "Google": {"query": "test"},
        "WeatherForecast24H": {"location": "101010100"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "SunriseSunset": {"location": "101010100"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "WeatherForecast3D": {"location": "101010100"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "WeatherForecast7D": {"location": "101010100"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "WeatherIndex1D": {"location": "101010100"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "WeatherRainMinute": {"location": "101010100"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "SearchLocation": {"location": "101010100"},
        "SearchHotelDestination": {"destination": "101010100"},
        "SearchHotels": {"destination": "101010100", "checkin": "2024-07-01", "checkout": "2024-07-10"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "SearchFlightLocation": {"location": "101010100"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "SearchFlightsMinPrice": {"from": "101010100", "to": "Los Angeles"},
        "SearchFlights": {"from": "101010100", "to": "Los Angeles", "date": "2024-07-01"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "GetCurrency": {"currency": "USD"},
        "GetExchangeRates": {"from": "USD", "to": "EUR"},
        "LocationToLatLon": {"location": "101010100"},
        "FanFavorites": {},
        "SearchIMDB": {"query": "Inception"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "Top100Movies": {},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "Top100Series": {},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "UpcomingMovies": {},
        "WeekTop10": {},
        "WhatsStreaming": {},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "GetCurrentTime": {},
        "GetCurrentDate": {},
        "CalcDatetime": {"date": "2024-07-01"},  # TODO: 错误代码: Failed tool. 可能的错误：参数问题或API不可用。
        "AmazonProductByCategory": {"category_id": "2478868012", "page": 1, "country": "US", "sort_by": "RELEVANCE", "product_condition": "ALL"},
        "AmazonProductDetails": {"asin": "B07ZPKBL9V", "country": "US"},
        "AmazonProductReviews": {"asin": "B07ZPKN6YR", "country": "US", "sort_by": "TOP_REVIEWS", "star_rating": "ALL", "verified_purchases_only": False, "images_or_videos_only": False, "current_format_only": False, "page": 1},
        "AmazonProductSearch": {"query": "Phone", "page": 1, "country": "US", "sort_by": "RELEVANCE", "product_condition": "ALL"},
        "GoogleNewsBusiness": {"language": "en-US"},  # TODO: 错误代码400. 可能的错误：请求参数错误。
        "GoogleNewsEntertainment": {"language": "en-US"},  # TODO: 错误代码400. 可能的错误：请求参数错误。
        "GoogleNewsLatest": {"language": "en-US"},  # TODO: 错误代码429. 可能的错误：请求频率限制。
        "GoogleNewsScience": {"language": "en-US"},  # TODO: 错误代码400. 可能的错误：请求参数错误。
        "GoogleNewsSearch": {"keyword": "facebook", "language": "en-US"},  # TODO: 错误代码504. 可能的错误：服务器网关超时。
        "GoogleNewsSport": {"language": "en-US"},  # TODO: 错误代码400. 可能的错误：请求参数错误。
        "GoogleNewsSuggest": {"keyword": "facebook", "language": "en-US"},  # TODO: 错误代码504. 可能的错误：服务器网关超时。
        "GoogleNewsTechnology": {"language": "en-US"},  # TODO: 错误代码400. 可能的错误：请求参数错误。
        "GoogleNewsWorld": {"language": "en-US"},  # TODO: 错误代码400. 可能的错误：请求参数错误。
        "LinkedInGetCompanyByUrl": {"linkedin_url": "https://www.linkedin.com/company/apple/"},  # TODO: 错误代码400. 可能的错误：请求参数错误。
        "LinkedInGetPersonalProfile": {"profile_url": "https://www.linkedin.com/in/sample-profile/"},  # TODO: 错误代码404. 可能的错误：资源未找到。
        "LinkedInSearchJobs": {
            "geo_code": "103644278",
            "function_id": "it,sale",
            "industry_code": "4,5",
            "date_posted": "any_time",
            "sort_by": "most_relevant",
            "start": 0,
            "easy_apply": False,
            "under_10_applicants": False
        },  # TODO: 错误代码：参数缺失。 可能的错误：缺少必要参数function_id和industry_code。
        "FilterByArea": {"area": "Seafood"},  # TODO: 错误代码200. 可能的错误：请求参数错误，返回meals为None。
        "FilterByCategory": {"category": "Seafood"},  # TODO: 错误代码200. 可能的错误：请求参数错误，返回meals为None。
        "FilterByMainIngredient": {"ingredient": "chicken_breast"},  # TODO: 错误代码200. 可能的错误：请求参数错误，返回meals为None。
        "FilterByMultiIngredient": {"ingredients": "chicken_breast,garlic,salt"}  # TODO: 错误代码200. 可能的错误：请求参数错误，返回meals为None。
    }

    failed_tools = []

    for tool, tool_input in tools.items():
        try:
            result = use_actual_tool(tool, tool_input)
            if not result:
                failed_tools.append(tool)
        except Exception as e:
            print(f"Tool {tool} failed with exception: {e}")
            failed_tools.append(tool)

    if failed_tools:
        print("Failed tools:", failed_tools)
    else:
        print("All tools executed successfully.")

if __name__ == "__main__":
    test_all_tools()
