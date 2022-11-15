import logging
from tefnut.utils.setting import settings


def pytest_configure(config):
    logger = logging.getLogger("main")
    logger.info("Configuring test")
    settings.set("loki.enable", False, persist=False)
    settings.set("INFLUX.enable", False, persist=False)
    settings.set("GENERAL.delta", 2, persist=False)


def pytest_sessionfinish(session):
    import tefnut.control.control as control
    logger = logging.getLogger("main")
    logger.info("test finished")
    control.humidificator.shutdown()
