import logging
import time
import psutil
import atexit
from tefnut.utils.constant import STATE, MODE
from tefnut.utils.setting import settings
from tefnut.control.weather import get_temperature
from tefnut.control.ecobee import get_pin, ecobee as ee
from tefnut.utils.influx_client import InfluxClient
from tefnut.control.humidificator import Humidificator
from influxdb_client import Point


logger = logging.getLogger("main")
influx_client = InfluxClient()
humidificator = Humidificator()
DELAY_LOOP = 60
DELAY_TEMP = 15 * 60
TEMP_EMERGENCY_DELAY = 3 * 60 * 60  # 3 hours
DELAY_HUMIDITY = 10 * 60
HUMIDITY_EMERGENCY_DELAY = 40 * 60  # 40 min


state = {'temp time': time.time() - DELAY_TEMP,
         'humidity time': time.time() - DELAY_HUMIDITY,
         'temp delay': 0,
         'humidity delay': 0,
         'current_temp': None,
         'future_temp': None,
         'target_temp': None,
         'humidity': None,
         'target_humidity': settings.get("GENERAL.manual_target"),
         'mode': MODE.AUTO,
         'state': STATE.OFF,
         }
ecobee = None


def compute_automated_target(outside_temp):
    if outside_temp >= 3:
        return 45
    elif outside_temp >= -12:
        return 40
    elif outside_temp >= -18:
        return 35
    elif outside_temp >= -24:
        return 25
    elif outside_temp >= -30:
        return 20
    else:
        return 15


def humidificator_controller():
    logger.debug("Starting control")
    if state['humidity'] is not None:
        logger.debug("humidity is currently %d", state['humidity'])
    output = 0
    if any(value is None for value in state.values()):
        logger.error("None values in dict when making decision")
        return -1

    state['mode'] = MODE[settings.get("GENERAL.mode")]

    if state['humidity delay'] >= HUMIDITY_EMERGENCY_DELAY:
        logger.error("No Humidity info for too long, turning Humi off")
        state['mode'] = MODE.NO_HUMIDITY
        humidificator.turn_off()
        logger.info("Stopping Thermostat")
        state['state'] = STATE.OFF
        return -2

    if state['temp delay'] >= TEMP_EMERGENCY_DELAY and state['mode'] == MODE.AUTO:
        logger.error("No temp info for too long, running in emerengy target")
        state['mode'] = MODE.TEMP_EMERGENCY
        settings.set("GENERAL.mode", MODE.TEMP_EMERGENCY.name, persist=False)
        state['target_humidity'] = settings.get("GENERAL.emergency_target")
        output = -5

    if state['mode'] == MODE.MANUAL:
        state['target_humidity'] = settings.get("GENERAL.manual_target")
        logger.debug("Manual")
    elif state['mode'] == MODE.AUTO:
        logger.debug("Auto")
        state['target_humidity'] = compute_automated_target(state['target_temp'])

    if state['humidity'] <= state['target_humidity'] - settings.get("GENERAL.delta") and state['state'] != STATE.ON:
        humidificator.turn_on()
        logger.info("Starting Thermostat")
        state['state'] = STATE.ON
        output += 1
    elif state['humidity'] > state['target_humidity'] + settings.get("GENERAL.delta") and state['state'] != STATE.OFF:
        humidificator.turn_off()
        logger.info("Stopping Thermostat")
        state['state'] = STATE.OFF
        output += 2

    logger.debug("Mode %s", state['mode'].name)
    logger.debug("State %s", state['state'].name)
    logger.debug("Target Humidity %d", state['target_humidity'])

    if state['state'] == humidificator.get_value():
        logger.debug("Humidificator and Logic are in sync")
    else:
        logger.error("Humidificator and Logic are not in sync")
        return -6
    return output


def data_collection_logic(current_values):

    # humidity
    if "humidity" in current_values:
        if current_values['humidity'] is not None:
            if 'humidity time' in current_values and current_values['humidity time'] is not None:
                state['humidity time'] = current_values['humidity time']
                state['humidity delay'] = current_values['humidity delay']
            state['humidity'] = current_values['humidity']
            point = Point("humidity").field("humidity", float(current_values['humidity']))
            influx_client.write(point)

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
                state['temp delay'] = current_values['temp delay']
            state['current_temp'] = current_values['current_temp']
            state['future_temp'] = current_values['future_temp']
            state['target_temp'] = current_values['target_temp']

    humidificator_controller()

    point = (Point("humidity").field("target", float(state['target_humidity']))
             )
    influx_client.write(point)

    point = (Point("Status").field("mode", state['mode'].name)
                            .field("state", state['state'].name)
             )
    influx_client.write(point)

    point = (Point("hardware").field("cpu", float(psutil.cpu_percent()))
                              .field("ram", float(psutil.virtual_memory().percent))
             )
    influx_client.write(point)

    # Timings
    point = (Point("timming")
             .field("loop time", float(time.time()-current_values['start time']))
             .field("temp delay", float(current_values['temp delay']))
             .field("humidity delay", float(current_values['humidity delay']))
             )
    influx_client.write(point)
    return 0


def control_loop(name):
    try:
        logger.info("starting ecobee device")
        ecobee = ee()
        logger.info("Ecobee device started")
    except Exception:
        logger.error("Failed to load Ecobee, Please validate PIN %s", get_pin())

    try:
        while True:
            current_values = {}
            current_values['start time'] = time.time()
            logger.debug("starting a control loop")
            current_values['temp delay'] = time.time() - state['temp time']
            current_values['humidity delay'] = time.time() - state['humidity time']

            # humidity
            if current_values['humidity delay'] >= DELAY_HUMIDITY:
                logger.info("Capturing humidity")
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

            data_collection_logic(current_values)

            time.sleep(DELAY_LOOP)

    except Exception as e:
        logger.fatal("control main loop exception", exc_info=e)
    finally:
        logger.info("control main loop finish")
        humidificator.shutdown()


@atexit.register
def goodbye():
    humidificator.shutdown()
