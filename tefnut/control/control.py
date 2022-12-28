import logging
import time

import psutil
from influxdb_client import Point

from tefnut.control.ecobee import ecobee as ee
from tefnut.control.humidifier import Humidifier
from tefnut.control.weather import get_temperature
from tefnut.utils.constant import MODE, STATE
from tefnut.utils.influx_client import InfluxClient
from tefnut.utils.setting import settings

logger = logging.getLogger("main")
influx_client = InfluxClient()
looping = True
DELAY_LOOP = 60
DELAY_TEMP = 15 * 60
TEMP_EMERGENCY_DELAY = 3 * 60 * 60  # 3 hours
HUMIDITY_EMERGENCY_DELAY = 20 * 60  # 40 min

humidifier = Humidifier()

OFF_DELAY_HUMIDITY = 5 * 60 - 2
ON_DELAY_HUMIDITY = 1 * 60 - 2


class TefnutController:
    state = {'temp time': time.time() - DELAY_TEMP,
             'humidity time': time.time() - OFF_DELAY_HUMIDITY,
             'temp delay': 0,
             'humidity delay': 0,
             'current_temp': None,
             'future_temp': None,
             'target_temp': None,
             'humidity': None,
             'target_humidity': settings.get("GENERAL.manual_target", default=40),
             'auto_delta': settings.get("GENERAL.auto_delta", default=0),
             'mode': MODE.AUTO,
             'state': STATE.OFF,
             }

    def __init__(self):
        self.humidifier = humidifier

        logger.info("starting ecobee device")
        self.ecobee = ee("pyecobee_db")
        logger.info("Ecobee device started")
        self._is_active = self.ecobee.is_active()

    def is_active(self):
        return self._is_active

    def controler_loop(self):
        try:
            current_values = {}
            current_values['start time'] = time.time()
            logger.debug("starting a control loop")
            self.state['temp delay'] = time.time() - self.state['temp time']
            self.state['humidity delay'] = time.time() - self.state['humidity time']

            # humidity
            delay = ON_DELAY_HUMIDITY if self.state["state"] == STATE.ON else OFF_DELAY_HUMIDITY
            if self.state['humidity delay'] >= delay:
                logger.info("Capturing humidity")
                current_values['humidity'] = self.ecobee.get_humidity()
                logger.debug("humidity: %s", current_values['humidity'])
                current_values['humidity time'] = time.time()
            else:
                logger.debug("Humidity fresh enough, not refreshing")

            # Weather
            if self.state['temp delay'] >= DELAY_TEMP:
                logger.info("Capturing temp")
                (current_values['current_temp'], current_values['future_temp'],
                    current_values['target_temp'], current_values['outdoor_humidity']) = get_temperature()
                logger.debug("current temp: %s", current_values['current_temp'])
                logger.debug("forcast temp: %s", current_values['future_temp'])
                logger.debug("target temp: %s", current_values['target_temp'])
                logger.debug("Outdoor Humidity: %s", current_values['outdoor_humidity'])
                current_values['temp time'] = time.time()
            else:
                logger.debug("Temp fresh enough, not refreshing")

            self.data_collection_logic(current_values)

        except Exception as e:
            logger.fatal("control main loop exception", exc_info=e)

    def goodbye(self):
        logger.info("GOODBYE")
        self.humidifier.shutdown()

    def humidifier_controller(self):
        logger.debug("Starting control")
        if self.state['humidity'] is not None:
            logger.debug("humidity is currently %d", self.state['humidity'])
        output = 0
        if any(value is None for value in self.state.values()):
            logger.error("None values in dict when making decision")
            return -1

        self.state['mode'] = MODE[settings.get("GENERAL.mode")]
        self.state['auto_delta'] = settings.get("GENERAL.auto_delta", default=0)

        if self.state['humidity delay'] >= HUMIDITY_EMERGENCY_DELAY:
            logger.error("No Humidity info for too long, turning Humi off")
            self.state['mode'] = MODE.NO_HUMIDITY
            self.humidifier.turn_off()
            logger.info("Stopping Humidifier")
            self.state['state'] = STATE.OFF
            return -2

        if self.state['temp delay'] >= TEMP_EMERGENCY_DELAY and self.state['mode'] == MODE.AUTO:
            logger.error("No temp info for too long, running in emerengy target")
            self.state['mode'] = MODE.TEMP_EMERGENCY
            settings.set("GENERAL.mode", MODE.TEMP_EMERGENCY.name, persist=False)
            self.state['target_humidity'] = settings.get("GENERAL.emergency_target", default=30)
            output = -5

        if self.state['mode'] == MODE.MANUAL:
            self.state['target_humidity'] = settings.get("GENERAL.manual_target", default=40)
            logger.debug("Manual")
        elif self.state['mode'] == MODE.AUTO:
            logger.debug("Auto")
            tmp_target = self.compute_automated_target(self.state['target_temp'])
            if tmp_target is not None:  # Leaving a deadspot for specific degree
                self.state['target_humidity'] = self.compute_automated_target(self.state['target_temp'])
        elif self.state['mode'] == MODE.OFF:
            logger.debug("Off")
            self.humidifier.turn_off()
            self.state['state'] = STATE.OFF
            return -7

        deadband = settings.get("GENERAL.deadband", default=2)

        if self.state['humidity'] < self.state['target_humidity'] - deadband and self.state['state'] != STATE.ON:
            self.humidifier.turn_on()
            logger.info("Starting Humidifier")
            self.state['state'] = STATE.ON
            output += 1
        elif self.state['humidity'] > self.state['target_humidity'] + deadband and self.state['state'] != STATE.OFF:
            self.humidifier.turn_off()
            logger.info("Stopping Humidifier")
            self.state['state'] = STATE.OFF
            output += 2

        logger.debug("Mode %s", self.state['mode'].name)
        logger.debug("State %s", self.state['state'].name)
        logger.debug("Target Humidity %d", self.state['target_humidity'])

        if self.state['state'] == self.humidifier.get_value():
            logger.debug("Humidifier and Logic are in sync")
        else:
            logger.error("Humidifier and Logic are not in sync")
            return -6
        return output

    def data_collection_logic(self, current_values):

        # humidity
        if "humidity" in current_values:
            if current_values['humidity'] is not None:
                if 'humidity time' in current_values and current_values['humidity time'] is not None:
                    self.state['humidity time'] = current_values['humidity time']
                self.state['humidity'] = current_values['humidity']
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

                point = (Point("humidity").field("outdoor", float(current_values['outdoor_humidity'])))
                influx_client.write(point)

                if 'temp time' in current_values and current_values['temp time'] is not None:
                    self.state['temp time'] = current_values['temp time']
                self.state['current_temp'] = current_values['current_temp']
                self.state['future_temp'] = current_values['future_temp']
                self.state['target_temp'] = current_values['target_temp']

        self.humidifier_controller()

        hum_state = 100 if self.state['state'] == STATE.ON else 0

        point = (Point("humidity").field("target", float(self.state['target_humidity']))
                                  .field("state", float(hum_state))
                                  .field("delta", float(self.state['auto_delta'])))
        influx_client.write(point)

        point = (Point("Status").field("mode", self.state['mode'].name)
                                .field("state", self.state['state'].name))
        influx_client.write(point)

        point = (Point("hardware").field("cpu", float(psutil.cpu_percent()))
                                  .field("ram", float(psutil.virtual_memory().percent)))
        influx_client.write(point)

        # Timings
        point = (Point("timming")
                 .field("loop time", float(time.time()-current_values['start time']))
                 .field("temp delay", float(self.state['temp delay']))
                 .field("humidity delay", float(self.state['humidity delay'])))
        influx_client.write(point)
        return 0

    def compute_automated_target(self, outside_temp):
        outside_temp = int(outside_temp)
        delta = settings.get("GENERAL.auto_delta", default=0)

        if outside_temp > 5:
            return 45 + delta
        elif outside_temp > -10 and outside_temp < 5:
            return 40 + delta
        elif outside_temp > -15 and outside_temp < -10:
            return 35 + delta
        elif outside_temp > -20 and outside_temp < -15:
            return 30 + delta
        elif outside_temp > -25 and outside_temp < -20:
            return 25 + delta
        elif outside_temp > -30 and outside_temp < -25:
            return 20 + delta
        elif outside_temp < -30:
            return 15 + delta
        else:
            return None
