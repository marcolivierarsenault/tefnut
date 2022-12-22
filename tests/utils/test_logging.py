import logging
from tefnut.utils.setting import settings
from tefnut.utils.logging import configure_logger


def test_disable_loki():
    configure_logger(logging.getLogger("test_disable_loki"))
    assert len(logging.getLogger("test_disable_loki").handlers) == 1


def test_enable_loki():
    settings.set("loki.enable", True, persist=False)
    configure_logger(logging.getLogger("test_enable_loki"))
    assert len(logging.getLogger("test_enable_loki").handlers) == 2
