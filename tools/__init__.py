## 导入所有的工具类
from .qweather_water_level import waterlevelcheck, WaterLevelSchema
from tools.demo_search_weather import search_weather, WeatherInput
from tools.qweather_search_location import search_location, LocationInput
from tools.qweather_sunrise_sunset import sunrise_sunset, WeatherInput
from tools.qweather_weather_forcast_24h import weather_forcast_24h
from tools.qweather_weather_rain_minute import weather_rain_minute
from tools.qweather_weather_forcast_3d import weather_forcast_3d
from tools.qweather_weather_forcast_7d import weather_forcast_7d
from tools.qweather_weather_index_1d import weather_index_1d
from tools.get_current_time import get_current_time, TimeInput
from tools.bookings_get_currency import get_currency
from tools.bookings_get_exchange_rates import get_exchange_rates
from tools.bookings_get_languages import get_languages
from tools.bookings_location_to_lat_lon import get_location_to_lat_lon
from tools.bookings_search_attractions import search_attractions
from tools.bookings_search_flights import search_flights
from tools.bookings_search_hotels import search_hotels


