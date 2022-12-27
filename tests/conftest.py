import logging
from tefnut.utils.setting import settings


def pytest_configure(config):
    logger = logging.getLogger("main")
    logger.info("Configuring test")
    settings.set("loki.enable", False, persist=False)
    settings.set("INFLUX.enable", False, persist=False)
    settings.set("GENERAL.deadband", 2, persist=False)
    settings.set("GENERAL.humidifier", "stub", persist=False)
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.auto_delta", 0, persist=False)
    settings.set("ECOBEE.apikey", "dsaDwe34fDsfedsssd3dasADWDqwdawd", persist=False)
    settings.set("WEBUI.username", "test", persist=False)
    settings.set("WEBUI.password", "test", persist=False)


def pytest_sessionfinish(session):
    import tefnut.control.control as control
    logger = logging.getLogger("main")
    logger.info("test finished")
    control.TefnutController().humidifier.shutdown()
