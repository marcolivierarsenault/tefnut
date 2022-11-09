import logging
import time
from tefnut.utils.setting import settings

logger = logging.getLogger("main")


def control_loop(name):
    try:
        while True:
            logger.info(settings.get("general.test"))
            time.sleep(1)

            # Weather

    except Exception as e:
        logger.error("control main loop exception")
        logger.error(e)
    finally:
        logger.info("control main loop finish")
