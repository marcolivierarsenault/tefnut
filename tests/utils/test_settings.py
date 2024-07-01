import os

import pytest

from tefnut.utils.setting import SettingLoader, settings


def test_missing_path(caplog):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        SettingLoader("wrong")
    assert pytest_wrapped_e.type is SystemExit
    assert "CONFIG FILE DOES NOT EXISTS, please a add settings.toml" in caplog.text


def test_write():
    open("test_conf.toml", "a").close()
    set_client = SettingLoader("test_conf.toml")
    set_client.set("test.test", "123", True)
    assert set_client.get("test.test") == "123"
    os.remove("test_conf.toml")


def test_missing_value():
    assert settings.get("does_not_exist") is None


def test_missing_value_with_default():
    assert settings.get("does_not_exist", default="test") == "test"


def test_getter_setter():
    assert settings.get("new_value") is None
    settings.set("new_value", "123", False)
    assert settings.get("new_value") == "123"
