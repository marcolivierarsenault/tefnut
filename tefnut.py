"""
Tenut
"""
import logging
import threading
from tefnut.control import control
from tefnut.utils.logging import configure_logger

logger = logging.getLogger("main")

if __name__ == "__main__":
    logger.info("++++++++++Tefnut application starting++++++++++")
    configure_logger()
    logger.debug("Starting control loop")
    x = threading.Thread(target=control.control_loop, args=(1,))
    x.start()
