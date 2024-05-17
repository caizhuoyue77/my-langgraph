
# 把对应的工具import进来
from langchain_community.tools.tavily_search import TavilySearchResults
from tools.get_current_time import get_current_time
from tools.bookings_get_currency import get_currency
from tools.bookings_get_exchange_rates import get_exchange_rates
from tools.bookings_get_languages import get_languages
from tools.bookings_location_to_lat_lon import location_to_lat_lon
from tools.bookings_search_attraction_locations import search_attraction_locations
from tools.bookings_search_attractions import search_attractions
from tools.bookings_search_flight_location import search_flight_location
from tools.bookings_search_flights_min_price import search_flights_min_price
from tools.bookings_search_flights import search_flights
from tools.bookings_search_hotel_destination import search_hotel_destination
from tools.bookings_search_hotels import search_hotels
from tools.qweather_search_location import search_location
from tools.qweather_sunrise_sunset import sunrise_sunset
from tools.qweather_water_level import water_level
from tools.qweather_weather_forcast_3d import weather_forcast_3d
from tools.qweather_weather_forcast_7d import weather_forcast_7d
from tools.qweather_weather_forcast_24h import weather_forcast_24h
from tools.qweather_weather_index_1d import weather_index_1d
from tools.qweather_weather_rain_minute import weather_rain_minute
from tools.imdb_born_on import born_on
from tools.imdb_fan_favorite import fan_favorite
from tools.imdb_search_imdb import search_imdb
from tools.imdb_top_100_movies import top_100_movies
from tools.imdb_top_100_series import top_100_series
from tools.imdb_upcoming_movies import upcoming_movies
from tools.imdb_week_top_10 import week_top_10
from tools.imdb_whats_streaming import whats_streaming

def use_actual_tool(tool: str, tool_input: dict):
    search = TavilySearchResults()

    # 通用API
    if tool == "Google":
        result = search.invoke(tool_input)
    # 天气API
    elif tool == "WeatherSearch":
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
    elif tool == "WaterLevel":
        result = water_level(tool_input)
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
    elif tool == "FanFavorite":
        result = fan_favorite(tool_input)
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