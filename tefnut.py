"""
Tenut
"""
import logging
import threading
import git
import tefnut.webui.webservice as webservice
from tefnut.control import control
from tefnut.utils.logging import configure_logger

logger = logging.getLogger("main")


def start_control():
    logger.debug("Starting control loop")
    x = threading.Thread(target=control.control_loop, args=(1,))
    x.start()


def start_webui():
    logger.debug("Starting WebUI")
    configure_logger(webservice.app.logger)
    webservice.app.run(host='0.0.0.0', debug=True)


if __name__ == "__main__":
    logger.info("++++++++++Tefnut application starting++++++++++")
    configure_logger(logger)

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    logger.info("Starting code on git sha: %s", sha)
    
    start_control()
    start_webui()
