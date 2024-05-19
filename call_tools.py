# 把对应的工具import进来
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config_api_keys import TAVILY_API_KEY, OPENAI_API_KEY
from langchain_community.tools.tavily_search import TavilySearchResults

import sys
import os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将tools目录添加到sys.path中
tools_dir = os.path.join(current_dir, 'tools')
sys.path.append(tools_dir)

from get_current_time import get_current_time
from bookings_get_currency import get_currency
from bookings_get_exchange_rates import get_exchange_rates
from bookings_get_languages import get_languages
from bookings_location_to_lat_lon import location_to_lat_lon
from bookings_search_attraction_locations import search_attraction_locations
from bookings_search_attractions import search_attractions
from bookings_search_flight_location import search_flight_location
from bookings_search_flights_min_price import search_flights_min_price
from bookings_search_flights import search_flights
from bookings_search_hotel_destination import search_hotel_destination
from bookings_search_hotels import search_hotels
from qweather_search_location import search_location
from qweather_sunrise_sunset import sunrise_sunset
from qweather_weather_forcast_3d import weather_forcast_3d
from qweather_weather_forcast_7d import weather_forcast_7d
from qweather_weather_forcast_24h import weather_forcast_24h
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
    # TODO:待添加，实时天气查询
    # elif tool == "CurrentWeather":
        # result = current_weather(tool_input)
    # 24小时内的天气预报
    elif tool == "WeatherSearch":
        return "长沙现在的天气是晴天，温度是25摄氏度，湿度是50%。"
        result = weather_forcast_24h(tool_input)
    elif tool == "SunriseSunset":
        result = sunrise_sunset(tool_input)
    elif tool == "WeatherForecast3D":
        result = weather_forcast_3d(tool_input)
    elif tool == "WeatherForecast7D":
        result = weather_forcast_7d(tool_input)
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
    elif tool == "GetLanguages":
        result = get_languages(tool_input)
    elif tool == "LocationToLatLon":
        result = location_to_lat_lon(tool_input)
    elif tool == "SearchAttractionLocations":
        result = search_attraction_locations(tool_input)
    elif tool == "SearchAttractions":
        result = search_attractions(tool_input)
    # IMDb 电影/电视剧API
    elif tool == "BornOn":
        result = born_on(tool_input)
    elif tool == "FanFavorites":
        result = fan_favorites(tool_input)
    elif tool == "SearchIMDb":
        result = search_imdb(tool_input)
    elif tool == "Top100Movies":
        result = top_100_movies(tool_input)
    elif tool == "Top100Series":
        result = top_100_series(tool_input)
    elif tool == "UpcomingMovies":
        result = upcoming_movies(tool_input)
    elif tool == "WeekTop10":
        result = week_top_10(tool_input)
    elif tool == "WhatsStreaming":
        result = whats_streaming(tool_input)
    # 自己编写的API
    elif tool == "GetCurrentTime":
        result = get_current_time()
    else:
        raise ValueError(f"Unknown tool: {tool}")

    return result