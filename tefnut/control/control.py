import logging
import time
# from tefnut.utils.setting import settings
from tefnut.control.weather import get_temperature
from tefnut.control.ecobee import ecobee as ee
from tefnut.utils.influx_client import InfluxClient
from influxdb_client import Point

logger = logging.getLogger("main")
influx_client = InfluxClient()
DELAY_LOOP = 60
DELAY_TEMP = 15 * 60
TEMP_EMERGENCY_DELAY = 3 * 60 * 60  # 3 hours
DELAY_HUMIDITY = 10 * 60
HUMIDITY_EMERGENCY_DELAY = 40 * 60  # 40 min
state = {'temp time': time.time() - DELAY_TEMP,
         'humidity time': time.time() - DELAY_HUMIDITY}
ecobee = None


def data_collection_logic(current_values):

    # humidity
    if "humidity" in current_values:
        if current_values['humidity'] is not None:
            point = (Point("humidity").field("humidity", float(current_values['humidity'])))
            influx_client.write(point)
            if 'humidity time' in current_values and current_values['humidity time'] is not None:
                state['humidity time'] = current_values['humidity time']
            state['humidity'] = current_values['humidity']

    # temp
    if all(["current_temp" in current_values,
            "future_temp" in current_values,
            "target_temp" in current_values]):

        if all([current_values['current_temp'] is not None,
                current_values['future_temp'] is not None,
                current_values['target_temp'] is not None]):

            point = (Point("temp")
                     .field("current temp", float(current_values['current_temp']))
                     .field("forcast temp", float(current_values['future_temp']))
                     .field("target temp", float(current_values['target_temp']))
                     )
            influx_client.write(point)
            if 'temp time' in current_values and current_values['temp time'] is not None:
                state['temp time'] = current_values['temp time']
            state['current_temp'] = current_values['current_temp']
            state['future_temp'] = current_values['future_temp']
            state['target_temp'] = current_values['target_temp']

    # Timings
    point = (Point("timming")
             .field("loop time", float(current_values['finish time']-current_values['start time']))
             .field("temp delay", float(current_values['temp delay']))
             .field("humidity delay", float(current_values['humidity delay']))
             )
    influx_client.write(point)
    return 0


def control_loop(name):
    try:
        logger.debug("starting ecobee device")
        ecobee = ee()
        logger.debug("Ecobee device started")
    except Exception as e:
        logger.fatal("Failed to load Ecobee, Please validate PIN ")
        logger.fatal(e)

    try:
        while True:
            current_values = {}
            current_values['start time'] = time.time()
            logger.debug("starting a control loop")
            current_values['temp delay'] = time.time() - state['temp time']
            current_values['humidity delay'] = time.time() - state['humidity time']

            # humidity
            if current_values['humidity delay'] >= DELAY_HUMIDITY:
                current_values['humidity'] = ecobee.get_humidity()
                logger.debug("humidity: %s", current_values['humidity'])
                current_values['humidity time'] = time.time()
            else:
                logger.info("Humidity fresh enough, not refreshing")

            # Weather
            if current_values['temp delay'] >= DELAY_TEMP:
                logger.info("Capturing temp")
                (current_values['current_temp'], current_values['future_temp'],
                 current_values['target_temp']) = get_temperature()
                logger.debug("current temp: %s", current_values['current_temp'])
                logger.debug("forcast temp: %s", current_values['future_temp'])
                logger.debug("target temp: %s", current_values['target_temp'])
                current_values['temp time'] = time.time()
            else:
                logger.info("Temp fresh enough, not refreshing")

            current_values['finish time'] = time.time()
            data_collection_logic(current_values)

            time.sleep(DELAY_LOOP)

    except Exception as e:
        logger.error("control main loop exception")
        logging.error(e)
    finally:
        logger.info("control main loop finish")
