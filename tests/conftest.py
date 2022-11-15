import logging
from tefnut.utils.setting import settings
import tefnut.control.control as control


def pytest_sessionstart(session):
    logger = logging.getLogger("main")
    logger.info("Configuring test")
    settings.set("loki.enable", False, persist=False)
    settings.set("INFLUX.enable", False, persist=False)
    settings.set("GENERAL.delta", 2, persist=False)


def pytest_sessionfinish(session):
    logger = logging.getLogger("main")
    logger.info("test finished")
    control.humidificator.shutdown()
