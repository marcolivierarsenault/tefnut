import logging

from tefnut.utils.constant import STATE

logger = logging.getLogger("main")


class HumidifierImplement:
    def __init__(self):
        logger.info("Using Stub humidifier")
        self.state = STATE.OFF

    def turn_on(self):
        logger.info("Turning On humidifier")
        self.state = STATE.ON

    def turn_off(self):
        logger.info("Turning Off humidifier")
        self.state = STATE.OFF

    def get_value(self):
        logger.debug("Humidifier value is %s", self.state.name)
        return self.state

    def shutdown(self):
        logger.info("Shutdown humidifier, disabling GPIO")
        pass
