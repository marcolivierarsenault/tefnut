import logging
import logging_loki
from tefnut.utils.setting import settings

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# Console
handler2 = logging.StreamHandler()
logger.addHandler(handler2)

logger.info("setting logger")

if settings.loki.enable:
    handler = logging_loki.LokiHandler(
        url=settings.loki.url, 
        tags={"application": settings.loki.name},
        version="1",
    )
    logger.addHandler(handler)
    logger.info("Loki configured")

