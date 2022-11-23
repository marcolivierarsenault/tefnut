import logging
from tefnut.utils.logging import configure_logger


def test_disable_loki():
    configure_logger(logging.getLogger("main"))
    assert len(logging.getLogger("main").handlers) == 1
