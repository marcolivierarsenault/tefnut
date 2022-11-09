import requests
import json
import logging
from tefnut.utils.setting import settings

logger = logging.getLogger("main")


api_key = settings.get("WEATHER.api_key")
lat = settings.get("WEATHER.lat")
lon = settings.get("WEATHER.lon")

current_temp_url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
future_temp_url = "https://api.openweathermap.org/data/2.5/forecast?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)

current_temp = -100
future_temp = -100
target_temp = -100


def get_temperature():
    """
    This fetches the current weather and the 3 hour forcast.
    To save a bit on humidifier, we will not increase humidity if forecast shows that it will be a lot colder in 3 hours

    The target temperature represent the coldest value between current temperature and half way between current and
    forecasted temp

    return:
        tupple
        (current_temperature, 3_hour_forecast, target temperature)
    """
    # current temp
    try:
        response = requests.get(current_temp_url)
        logger.debug("response")
    except Exception as e:
        logger.error("Get Weather HTTP error")
        logger.error(e)

    if response.status_code != 200:
        logger.error("Error from the OpenWeather API, code code : %d", response.status_code)
    else:
        try:
            current_temp = json.loads(response.text)['main']['temp']
            logger.debug(current_temp)
        except Exception as e:
            logger.error(" Weather parsing JSON error")
            logger.error(e)

    # future temp
    try:
        response = requests.get(future_temp_url)
        logger.debug("response")
    except Exception as e:
        logger.error("Get Weather forecast HTTP error")
        logger.error(e)

    if response.status_code != 200:
        logger.error("Error from the OpenWeather forecast API, code code : %d", response.status_code)
    else:
        try:
            future_temp = json.loads(response.text)['list'][0]['main']['temp']
            logger.debug(future_temp)
        except Exception as e:
            logger.error(" Weather forecast parsing JSON error")
            logger.error(e)
