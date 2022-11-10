import logging
import time
# from tefnut.utils.setting import settings
from tefnut.control.weather import get_temperature
from tefnut.utils.influx_client import InfluxClient
from influxdb_client import Point

logger = logging.getLogger("main")
influx_client = InfluxClient()
DELAY_LOOP = 5
DELAY_HUMIDTY = 15
HUMIDITY_EMERGENCY_DELAY = 3 * 60 * 60  # 3 hours
state = {'humidity time': time.time()}


def humidificator_logic(current_values):
    if all(["current_temp" in current_values,
            "future_temp" in current_values,
            "target_temp" in current_values]):

        if all([current_values['current_temp'] is not None,
                current_values['future_temp'] is not None,
                current_values['target_temp'] is not None]):

            point = (Point("humidity")
                     .field("current temp", current_values['current_temp'])
                     .field("forcast temp", current_values['future_temp'])
                     .field("target temp", current_values['target_temp'])
                     )
            influx_client.write(point)
            state['humidity time'] = current_values['humidity time']
            state['current_temp'] = current_values['current_temp']
            state['future_temp'] = current_values['future_temp']

    point = (Point("timming")
             .field("loop time", current_values['finish time']-current_values['start time'])
             .field("humidity delay", current_values['humidity delay'])
             )
    influx_client.write(point)


def control_loop(name):
    try:
        while True:
            current_values = {}
            current_values['start time'] = time.time()
            current_values['humidity delay'] = time.time() - state['humidity time']
            logger.debug("starting a control loop")

            # Weather
            if current_values['humidity delay'] >= DELAY_HUMIDTY:
                logger.info("Capturing Humidity")
                (current_values['current_temp'], current_values['future_temp'],
                 current_values['target_temp']) = get_temperature()
                logger.debug("current temp: %s", current_values['current_temp'])
                logger.debug("forcast temp: %s", current_values['future_temp'])
                logger.debug("target temp: %s", current_values['target_temp'])
                current_values['humidity time'] = time.time()
            else:
                logger.info("Humidty fresh enough, not refreshing")

            current_values['finish time'] = time.time()
            humidificator_logic(current_values)

            time.sleep(DELAY_LOOP)

    except Exception as e:
        logger.error("control main loop exception")
        logger.error(e)
    finally:
        logger.info("control main loop finish")
