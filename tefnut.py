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
    x = threading.Thread(target=control.control_loop, daemon=True, args=(1,))
    x.start()


def start_webui(sha, version):
    logger.debug("Starting WebUI")
    webservice.sha = sha
    webservice.version = version
    configure_logger(webservice.app.logger)
    # webservice.app.run(use_debugger=False, use_reloader=False, passthrough_errors=True, host='0.0.0.0')  # For vsCode
    # webservice.app.run(host='0.0.0.0', debug=True)  # For normal debugging
    webservice.app.run(host='0.0.0.0', debug=False)  # For prod
    logger.info("stopping tefnut")
    control.goodbye()


if __name__ == "__main__":
    logger.info("++++++++++Tefnut application starting++++++++++")
    configure_logger(logger)

    f = open("VERSION", "r")
    version = f.read()
    f.close()

    logger.info("Tefnut version: %s", version)

    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha
    logger.info("Starting code on git sha: %s", sha)

    start_control()
    start_webui(sha, version)
