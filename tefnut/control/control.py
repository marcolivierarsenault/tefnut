import logging
import time
import psutil
import os
import atexit
from tefnut.utils.constant import STATE, MODE
from tefnut.utils.setting import settings
from tefnut.control.weather import get_temperature
from tefnut.control.ecobee import get_pin, ecobee as ee
from tefnut.utils.influx_client import InfluxClient
from tefnut.control.humidifier import Humidifier
from influxdb_client import Point


logger = logging.getLogger("main")
influx_client = InfluxClient()
humidifier = Humidifier()
DELAY_LOOP = 60
DELAY_TEMP = 15 * 60
TEMP_EMERGENCY_DELAY = 3 * 60 * 60  # 3 hours
HUMIDITY_EMERGENCY_DELAY = 20 * 60  # 40 min

OFF_DELAY_HUMIDITY = 5 * 60 - 2
ON_DELAY_HUMIDITY = 1 * 60 - 2


state = {'temp time': time.time() - DELAY_TEMP,
         'humidity time': time.time() - OFF_DELAY_HUMIDITY,
         'temp delay': 0,
         'humidity delay': 0,
         'current_temp': None,
         'future_temp': None,
         'target_temp': None,
         'humidity': None,
         'target_humidity': settings.get("GENERAL.manual_target", default=40),
         'mode': MODE.AUTO,
         'state': STATE.OFF,
         }
ecobee = None


def compute_automated_target(outside_temp):
    if outside_temp > 5:
        return 45
    elif outside_temp >= -9:
        return 40
    elif outside_temp >= -14:
        return 35
    elif outside_temp >= -19:
        return 30
    elif outside_temp >= -24:
        return 25
    elif outside_temp >= -29:
        return 20
    else:
        return 15


def humidifier_controller():
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
        humidifier.turn_off()
        logger.info("Stopping Humidifier")
        state['state'] = STATE.OFF
        return -2

    if state['temp delay'] >= TEMP_EMERGENCY_DELAY and state['mode'] == MODE.AUTO:
        logger.error("No temp info for too long, running in emerengy target")
        state['mode'] = MODE.TEMP_EMERGENCY
        settings.set("GENERAL.mode", MODE.TEMP_EMERGENCY.name, persist=False)
        state['target_humidity'] = settings.get("GENERAL.emergency_target", default=30)
        output = -5

    if state['mode'] == MODE.MANUAL:
        state['target_humidity'] = settings.get("GENERAL.manual_target", default=40)
        logger.debug("Manual")
    elif state['mode'] == MODE.AUTO:
        logger.debug("Auto")
        state['target_humidity'] = compute_automated_target(state['target_temp'])
    elif state['mode'] == MODE.OFF:
        logger.debug("Off")
        humidifier.turn_off()
        state['state'] = STATE.OFF
        return -7

    deadband = settings.get("GENERAL.deadband", default=2)

    if state['humidity'] < state['target_humidity'] - deadband and state['state'] != STATE.ON:
        humidifier.turn_on()
        logger.info("Starting Humidifier")
        state['state'] = STATE.ON
        output += 1
    elif state['humidity'] >= state['target_humidity'] + deadband and state['state'] != STATE.OFF:
        humidifier.turn_off()
        logger.info("Stopping Humidifier")
        state['state'] = STATE.OFF
        output += 2

    logger.debug("Mode %s", state['mode'].name)
    logger.debug("State %s", state['state'].name)
    logger.debug("Target Humidity %d", state['target_humidity'])

    if state['state'] == humidifier.get_value():
        logger.debug("Humidifier and Logic are in sync")
    else:
        logger.error("Humidifier and Logic are not in sync")
        return -6
    return output


def data_collection_logic(current_values):

    # humidity
    if "humidity" in current_values:
        if current_values['humidity'] is not None:
            if 'humidity time' in current_values and current_values['humidity time'] is not None:
                state['humidity time'] = current_values['humidity time']
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
            state['current_temp'] = current_values['current_temp']
            state['future_temp'] = current_values['future_temp']
            state['target_temp'] = current_values['target_temp']

    humidifier_controller()

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
             .field("temp delay", float(state['temp delay']))
             .field("humidity delay", float(state['humidity delay']))
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
            state['temp delay'] = time.time() - state['temp time']
            state['humidity delay'] = time.time() - state['humidity time']

            # humidity
            delay = ON_DELAY_HUMIDITY if state["state"] == STATE.ON else OFF_DELAY_HUMIDITY
            if state['humidity delay'] >= delay:
                logger.info("Capturing humidity")
                current_values['humidity'] = ecobee.get_humidity()
                logger.debug("humidity: %s", current_values['humidity'])
                current_values['humidity time'] = time.time()
            else:
                logger.info("Humidity fresh enough, not refreshing")

            # Weather
            if state['temp delay'] >= DELAY_TEMP:
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
        humidifier.shutdown()


@atexit.register
def goodbye():
    if "PYTEST_CURRENT_TEST" in os.environ:
        logger.warning("shutdown detected")
    humidifier.shutdown()
