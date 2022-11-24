# noqa: F401
import logging
import time
import RPi.GPIO as GPIO
from tefnut.utils.constant import STATE
from tefnut.utils.setting import settings

logger = logging.getLogger("main")


class HumidifierImplement:
    def __init__(self):
        logger.info("Using PI humidifier")
        self.pin = settings.get("GENERAL.rpi_pi")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(2)

    def turn_on(self):
        logger.info("Turning On Humidifier")
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(2)

    def turn_off(self):
        logger.info("Turning Off Humidifier")
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(2)

    def get_value(self):
        if 1 == GPIO.input(self.pin):
            logger.debug("Humidifier value is %s", STATE.OFF.name)
            return STATE.OFF
        logger.debug("Humidifier value is %s", STATE.ON.name)
        return STATE.ON

    def shutdown(self):
        logger.warning("Pi turning off the GPIO")
        GPIO.cleanup()
        time.sleep(2)
