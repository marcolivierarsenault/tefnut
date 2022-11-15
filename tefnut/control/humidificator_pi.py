# noqa: F401
import logging
import time
import RPi.GPIO as GPIO
from tefnut.utils.constant import STATE
from tefnut.utils.setting import settings

logger = logging.getLogger("main")


class HumidificatorImplement:
    def __init__(self):
        logger.info("Using PI humidificator")
        self.pin = settings.get("GENERAL.rpi_pi")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(0.5)

    def turn_on(self):
        logger.info("Turning On humidifcator")
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(0.5)

    def turn_off(self):
        logger.info("Turning Off humidifcator")
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(0.5)

    def get_value(self):
        if 1 == GPIO.input(self.pin):
            logger.debug("Humidificator value is %s", STATE.OFF.name)
            return STATE.OFF.name
        logger.debug("Humidificator value is %s", STATE.ON.name)
        return STATE.ON.name

    def shutdown(self):
        logger.info("Closing Humidificator")
        GPIO.cleanup()
        time.sleep(2)
