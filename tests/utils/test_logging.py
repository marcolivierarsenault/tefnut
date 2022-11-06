import logging
from tefnut.utils.setting import settings
from tefnut.utils.logging import configure_logger


def test_disable_loki():
    settings.set("loki.enable", False, persist=False)
    configure_logger()
    assert len(logging.getLogger("main").handlers) == 1
