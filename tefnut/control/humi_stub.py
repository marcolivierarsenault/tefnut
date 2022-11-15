import logging
from tefnut.utils.constant import STATE

logger = logging.getLogger("main")


class HumidificatorImplement:
    def __init__(self):
        logger.info("Using Stub humidificator")
        self.state = STATE.OFF

    def turn_on(self):
        logger.info("Turning On humidifcator")
        self.state = STATE.ON

    def turn_off(self):
        logger.info("Turning Off humidifcator")
        self.state = STATE.OFF

    def get_value(self):
        logger.debug("Humidificator value is %s", self.state.name)
        return self.state

    def shutdown(self):
        pass
