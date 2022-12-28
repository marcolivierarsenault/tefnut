import pytest

from tefnut.control.humidifier import Humidifier
from tefnut.utils.constant import STATE


@pytest.fixture
def humidifer():
    return Humidifier()


def test_turn_on(humidifer, caplog):
    humidifer.turn_on()
    assert 'Turning On humidifier' in caplog.text
    assert humidifer.get_value() == STATE.ON


def test_turn_off(humidifer, caplog):
    humidifer.turn_off()
    assert 'Turning Off humidifier' in caplog.text
    assert humidifer.get_value() == STATE.OFF


def test_shutdown(humidifer, caplog):
    humidifer.shutdown()
    assert 'Shutdown humidifier, disabling GPIO' in caplog.text
