import logging
import threading
from tefnut import control
from tefnut.utils.setting import settings, save_config
import tefnut.utils.logging

if __name__ == "__main__":
    logger = logging.getLogger("main")

    logger.info("Tefnut application starting")


    logger.info("Starting control loop")
    x = threading.Thread(target=control.main_loop, args=(1,))
    x.start()

    save_config()
    logger.info("Tefnut started")
    