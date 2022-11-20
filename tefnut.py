"""
Tenut
"""
import logging
import threading
import git
from tefnut.control import control
from tefnut.utils.logging import configure_logger

logger = logging.getLogger("main")

if __name__ == "__main__":
    logger.info("++++++++++Tefnut application starting++++++++++")
    configure_logger()

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    logger.info("Starting code on git sha: %s", sha)
    logger.debug("Starting control loop")
    x = threading.Thread(target=control.control_loop, args=(1,))
    x.start()
