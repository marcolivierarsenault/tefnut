import logging
import time
# from tefnut.utils.setting import settings
from tefnut.control.weather import get_temperature
from tefnut.utils.influx_client import InfluxClient
from influxdb_client import Point

logger = logging.getLogger("main")
influx_client = InfluxClient()
DELAY_LOOP = 5
DELAY_TEMP = 15
TEMP_EMERGENCY_DELAY = 3 * 60 * 60  # 3 hours
state = {'temp time': time.time() - DELAY_TEMP}


def humidificator_logic(current_values):
    if all(["current_temp" in current_values,
            "future_temp" in current_values,
            "target_temp" in current_values]):

        if all([current_values['current_temp'] is not None,
                current_values['future_temp'] is not None,
                current_values['target_temp'] is not None]):

            point = (Point("temp")
                     .field("current temp", current_values['current_temp'])
                     .field("forcast temp", current_values['future_temp'])
                     .field("target temp", current_values['target_temp'])
                     )
            influx_client.write(point)
            if 'temp time' in current_values and current_values['temp time'] is not None:
                state['temp time'] = current_values['temp time']
            state['current_temp'] = current_values['current_temp']
            state['future_temp'] = current_values['future_temp']
            state['target_temp'] = current_values['target_temp']

    point = (Point("timming")
             .field("loop time", current_values['finish time']-current_values['start time'])
             .field("temp delay", current_values['temp delay'])
             )
    influx_client.write(point)
    return 0


def control_loop(name):
    try:
        while True:
            current_values = {}
            current_values['start time'] = time.time()
            current_values['temps delay'] = time.time() - state['temps time']
            logger.debug("starting a control loop")

            # Weather
            if current_values['temps delay'] >= DELAY_TEMP:
                logger.info("Capturing temps")
                (current_values['current_temp'], current_values['future_temp'],
                 current_values['target_temp']) = get_temperature()
                logger.debug("current temp: %s", current_values['current_temp'])
                logger.debug("forcast temp: %s", current_values['future_temp'])
                logger.debug("target temp: %s", current_values['target_temp'])
                current_values['temps time'] = time.time()
            else:
                logger.info("Temp fresh enough, not refreshing")

            current_values['finish time'] = time.time()
            humidificator_logic(current_values)

            time.sleep(DELAY_LOOP)

    except Exception as e:
        logger.error("control main loop exception")
        logger.error(e)
    finally:
        logger.info("control main loop finish")
