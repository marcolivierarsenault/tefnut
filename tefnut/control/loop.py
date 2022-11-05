import logging
import threading
import time
from tefnut.utils.setting import settings

logger = logging.getLogger("main")

def main_loop(name):
    a = 3
    try:
        while True:
            logger.info("loop")
            time.sleep(1)
            a -= 1
            if a == 0:
                break
                raise Exception("snip")

    except Exception as e: 
        logger.error("control main loop exception")
        logger.error(e)
    finally:
        logger.info("control main loop finish")