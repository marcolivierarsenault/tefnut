import requests
import json
import logging
import time
from tefnut.utils.setting import settings

logger = logging.getLogger("main")


api_key = settings.get("WEATHER.api_key")
lat = settings.get("WEATHER.lat")
lon = settings.get("WEATHER.lon")

current_temp_url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
future_temp_url = "https://api.openweathermap.org/data/2.5/forecast?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)


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

    current_temp = None
    try:
        response = requests.get(current_temp_url)
        logger.debug(response)
    except Exception as e:
        logger.warning("Get Weather HTTP error", exc_info=e)
        return (None, None, None)

    if response.status_code != 200:
        logger.warning("Error from the OpenWeather API, code code : %d", response.status_code)
        return (None, None, None)
    else:
        try:
            current_temp = json.loads(response.text)['main']['temp']
            logger.debug(json.loads(response.text))
        except Exception as e:
            logger.warning(" Weather parsing JSON error", exc_info=e)
            return (None, None, None)

    # future temp
    future_temp = None
    try:
        response = requests.get(future_temp_url)
        logger.debug(response)
    except Exception as e:
        logger.warning("Get Weather forecast HTTP error", exc_info=e)
        return (None, None, None)

    if response.status_code != 200:
        logger.warning("Error from the OpenWeather forecast API, code code : %d", response.status_code)
        return (None, None, None)
    else:
        try:
            response = json.loads(response.text)
            current_time = int(time.time())
            logger.debug(response)
            # For some reason the open weather API, seems to be changing prediction in the last 1.5 hours of the 3 h windows
            if (60 * 60 * 1.5) + current_time < response['list'][0]['dt']:
                # Take first record, we are in the first 1.5 hour of the window
                future_temp = response['list'][0]['main']['temp']
                logger.debug("Taking first forecast")
            else:
                # Take second record, we are in the second 1.5 hour of the window
                future_temp = response['list'][1]['main']['temp']
                logger.debug("Taking second forecast")
        except Exception as e:
            logger.warning(" Weather forecast parsing JSON error", exc_info=e)
            return (None, None, None)

    if future_temp is not None and current_temp is not None:
        return (current_temp, future_temp, calculate_target(current_temp, future_temp))
    else:
        return (None, None, None)


def calculate_target(current_temp, future_temp):
    return min(current_temp, current_temp-(current_temp-future_temp)/2)
