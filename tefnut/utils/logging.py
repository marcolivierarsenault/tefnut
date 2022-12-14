"""Add logging and customize logging for the application."""
import logging

import logging_json
import logging_loki

from tefnut.utils.setting import settings


def configure_logger(logger):
    """Function to configure the logger"""
    logger.handlers.clear()
    logger.setLevel(settings.get("general.loglevel"))

    # Console
    handler2 = logging.StreamHandler()
    formatter2 = logging.Formatter(
        "%(asctime)s - %(module)10s - %(levelname)5s - %(message)s"
    )
    handler2.setFormatter(formatter2)
    logger.addHandler(handler2)

    logger.debug("setting logger")

    if settings.get("loki.enable"):
        logger.info("Enabling Loki")
        handler = logging_loki.LokiHandler(
            url=settings.get("loki.url"),
            tags={"application": settings.get("loki.name")},
            version="1",
        )
        # formatter = logging.Formatter('%(module)10s - %(levelname)5s - %(message)s')
        formatter = logging_json.JSONFormatter(
            fields={"severity": "levelname", "module": "module"}
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.info("Loki configured")
    else:
        logger.info("NOT Enabling Loki")
    logger.debug("Logging configured")
