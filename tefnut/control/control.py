import logging
import time
from tefnut.utils.setting import settings
from tefnut.control.weather import get_temperature

logger = logging.getLogger("main")


def control_loop(name):
    try:
        current_temp = -100
        future_temp = -100
        target_temp = -100
        while True:
            logger.info(settings.get("general.test"))

            # Weather
            (current_temp, future_temp, target_temp) = get_temperature()
            logger.info("current temp: %s", current_temp)
            logger.info("forcast temp: %s", future_temp)
            logger.info("target temp: %s", target_temp)

            time.sleep(5)

    except Exception as e:
        logger.error("control main loop exception")
        logger.error(e)
    finally:
        logger.info("control main loop finish")
