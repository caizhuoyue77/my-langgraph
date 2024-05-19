# 把对应的工具import进来
import os
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
    elif tool == "CurrentWeather":
        result = "长沙现在的天气是晴天，温度是25摄氏度，湿度是50%。"
        # result = current_weather(tool_input)
    # 24小时内的天气预报
    elif tool == "WeatherSearch":
        result = "未来24小时长沙的天气预报是晴天，最高温度27摄氏度，最低温度18摄氏度。"
        # result = weather_forcast_24h(tool_input)
    elif tool == "SunriseSunset":
        result = "今天在长沙的日出时间是5:05 AM，日落时间是6:45 PM。"
        # result = sunrise_sunset(tool_input)
    elif tool == "WeatherForecast3D":
        result = "未来三天长沙的天气预报是晴天为主，温度范围在17到28摄氏度之间。"
        # result = weather_forcast_3d(tool_input)
    elif tool == "WeatherForecast7D":
        result = "未来七天长沙的天气预报是晴天和多云交替，最高温度30摄氏度，最低温度15摄氏度。"
        # result = weather_forcast_7d(tool_input)
    elif tool == "WeatherIndex1D":
        result = "长沙今天的天气指数：空气质量良好，适合外出。"
        # result = weather_index_1d(tool_input)
    elif tool == "WeatherRainMinute":
        result = "未来60分钟内长沙无降雨。"
        # result = weather_rain_minute(tool_input)
    elif tool == "SearchLocation":
        result = "长沙的地理位置是纬度28.2282， 经度112.9388。"
        # result = search_location(tool_input)
    # 酒店API
    elif tool == "SearchHotelDestination":
        result = "您查询的酒店目的地为长沙，共有120家酒店供您选择。"
        # result = search_hotel_destination(tool_input)
    elif tool == "SearchHotels":
        result = "长沙的酒店搜索结果：共有120家酒店，价格范围从200到1000元每晚。"
        # result = search_hotels(tool_input)
    # 机票API
    elif tool == "SearchFlightLocation":
        result = "您查询的航班目的地为长沙，共有15个航班供您选择。"
        # result = search_flight_location(tool_input)
    elif tool == "SearchFlightsMinPrice":
        result = "从北京到长沙的最低机票价格为500元。"
        # result = search_flights_min_price(tool_input)
    elif tool == "SearchFlights":
        result = "从北京到长沙的航班搜索结果：共有15个航班，价格范围从500到1500元。"
        # result = search_flights(tool_input)
    # 货币/语言API
    elif tool == "GetCurrency":
        result = "当前的货币为人民币（CNY）。"
        # result = get_currency(tool_input)
    elif tool == "GetExchangeRates":
        result = "当前美元兑人民币的汇率为1:6.5。"
        # result = get_exchange_rates(tool_input)
    elif tool == "GetLanguages":
        result = "长沙的主要语言是中文。"
        # result = get_languages(tool_input)
    elif tool == "LocationToLatLon":
        result = "长沙的地理位置是纬度28.2282， 经度112.9388。"
        # result = location_to_lat_lon(tool_input)
    elif tool == "SearchAttractionLocations":
        result = "长沙的景点位置搜索结果：橘子洲、岳麓山、天心阁等。"
        # result = search_attraction_locations(tool_input)
    elif tool == "SearchAttractions":
        result = "长沙的景点搜索结果：橘子洲、岳麓山、天心阁等，共有30个景点。"
        # result = search_attractions(tool_input)
    # IMDb 电影/电视剧API
    elif tool == "BornOn":
        result = "您查询的生日为5月19日，出生在这一天的名人有：演员张艺谋。"
        # result = born_on(tool_input)
    elif tool == "FanFavorites":
        result = "当前的IMDB粉丝喜爱榜单包括《复仇者联盟》、《权力的游戏》等。"
        # result = fan_favorites(tool_input)
    elif tool == "SearchIMDB":
        result = "您查询的电影《复仇者联盟》在IMDB上的评分为8.4。"
        # result = search_imdb(tool_input)
    elif tool == "Top100Movies":
        result = "当前的IMDB电影前100名包括《肖申克的救赎》、《教父》等。"
        # result = top_100_movies(tool_input)
    elif tool == "Top100Series":
        result = "当前的IMDB电视剧前100名包括《权力的游戏》、《绝命毒师》等。"
        # result = top_100_series(tool_input)
    elif tool == "UpcomingMovies":
        result = "即将上映的电影包括《黑寡妇》、《速度与激情9》等。"
        # result = upcoming_movies(tool_input)
    elif tool == "WeekTop10":
        result = "本周IMDB排行榜前10名包括《复仇者联盟》、《权力的游戏》等。"
        # result = week_top_10(tool_input)
    elif tool == "WhatsStreaming":
        result = "当前热门的流媒体内容包括《曼达洛人》、《巫师》等。"
        # result = whats_streaming(tool_input)
    # 自己编写的API
    elif tool == "GetCurrentTime":
        result = "当前时间是2024年5月19日14:30。"
        # result = get_current_time()
    else:
        raise ValueError(f"Unknown tool: {tool}")

    return result