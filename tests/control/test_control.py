import time
from unittest.mock import patch

import pytest

import tefnut.control.control as tef_control
from tefnut.utils.setting import settings


@pytest.fixture
def state():
    return {
        "temp time": time.time() - tef_control.DELAY_TEMP,
        "humidity time": time.time() - tef_control.OFF_DELAY_HUMIDITY,
        "temp delay": 0,
        "humidity delay": 0,
        "current_temp": None,
        "future_temp": None,
        "target_temp": None,
        "humidity": None,
        "target_humidity": 40,
        "auto_delta": 0,
        "mode": tef_control.MODE.AUTO,
        "state": tef_control.STATE.OFF,
    }


@pytest.fixture
def state_with_data():
    return {
        "temp time": time.time() - tef_control.DELAY_TEMP,
        "humidity time": time.time() - tef_control.OFF_DELAY_HUMIDITY,
        "temp delay": 0,
        "humidity delay": 0,
        "current_temp": -20,
        "future_temp": -20,
        "target_temp": -20,
        "humidity": 40,
        "auto_delta": 0,
        "target_humidity": 30,
        "mode": tef_control.MODE.AUTO,
        "state": tef_control.STATE.OFF,
    }


@pytest.fixture
def current_values():
    return {
        "current_temp": 5,
        "future_temp": 6,
        "target_temp": 5.5,
        "finish time": time.time(),
        "start time": time.time() - 1,
        "temp time": time.time() - 0.5,
        "humidity time": time.time() - 0.5,
        "humidity freshness": time.time() - 0.5,
        "temp delay": 7,
        "humidity delay": 7,
        "humidity": 45,
        "outdoor_humidity": 60,
    }


@pytest.fixture
def control():
    return tef_control.TefnutController()


def test_normal_beavior(control, current_values, state):
    control.state = state
    assert control.data_collection_logic(current_values) == 0


def test_none_temp_setting(control, current_values, state):
    control.state = state

    current_values["current_temp"] = None
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] is None
    assert control.humidifier_controller() == -1

    current_values["future_temp"] = None
    control.data_collection_logic(current_values)
    assert control.state["future_temp"] is None
    assert control.humidifier_controller() == -1

    current_values["target_temp"] = None
    control.data_collection_logic(current_values)
    assert control.state["target_temp"] is None
    assert control.humidifier_controller() == -1

    del current_values["current_temp"]
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] is None
    assert control.humidifier_controller() == -1

    del current_values["future_temp"]
    control.data_collection_logic(current_values)
    assert control.state["future_temp"] is None
    assert control.humidifier_controller() == -1

    del current_values["target_temp"]
    control.data_collection_logic(current_values)
    assert control.state["target_temp"] is None
    assert control.humidifier_controller() == -1

    current_values["current_temp"] = 10
    current_values["future_temp"] = 11
    current_values["target_temp"] = 12
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12

    current_values["current_temp"] = None
    current_values["future_temp"] = None
    current_values["target_temp"] = None
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12

    del current_values["current_temp"]
    del current_values["future_temp"]
    del current_values["target_temp"]
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12


def test_none_temp_time(control, current_values, state):
    control.state = state
    init_time = control.state["temp time"]

    current_values["temp time"] = None
    control.data_collection_logic(current_values)
    assert init_time == control.state["temp time"]

    del current_values["temp time"]
    control.data_collection_logic(current_values)
    assert init_time == control.state["temp time"]

    current_values["temp time"] = init_time + 1
    control.data_collection_logic(current_values)
    assert init_time + 1 == control.state["temp time"]

    current_values["temp time"] = None
    control.data_collection_logic(current_values)
    assert init_time + 1 == control.state["temp time"]

    del current_values["temp time"]
    control.data_collection_logic(current_values)
    assert init_time + 1 == control.state["temp time"]


def test_none_humidity_setting(control, current_values, state):
    control.state = state

    current_values["humidity"] = None
    control.data_collection_logic(current_values)
    assert control.state["humidity"] is None
    assert control.humidifier_controller() == -1

    del current_values["humidity"]
    control.data_collection_logic(current_values)
    assert control.state["humidity"] is None
    assert control.humidifier_controller() == -1

    current_values["humidity"] = 10
    control.data_collection_logic(current_values)
    assert control.state["humidity"] == 10

    current_values["humidity"] = None
    control.data_collection_logic(current_values)
    assert control.state["humidity"] == 10

    del current_values["humidity"]
    control.data_collection_logic(current_values)
    assert control.state["humidity"] == 10


def test_none_humidity_time(control, current_values, state):
    control.state = state
    init_time = control.state["humidity time"]

    current_values["humidity time"] = None
    control.data_collection_logic(current_values)
    assert init_time == control.state["humidity time"]

    del current_values["humidity time"]
    control.data_collection_logic(current_values)
    assert init_time == control.state["humidity time"]

    current_values["humidity time"] = init_time + 1
    current_values["humidity freshness"] = init_time + 1
    control.data_collection_logic(current_values)
    assert init_time + 1 == control.state["humidity time"]

    current_values["humidity time"] = None
    current_values["humidity freshness"] = None
    control.data_collection_logic(current_values)
    assert init_time + 1 == control.state["humidity time"]

    del current_values["humidity time"]
    del current_values["humidity freshness"]
    control.data_collection_logic(current_values)
    assert init_time + 1 == control.state["humidity time"]

    current_values["humidity time"] = init_time + 100
    current_values["humidity freshness"] = init_time - 100
    control.data_collection_logic(current_values)
    assert init_time - 100 == control.state["humidity time"]


def test_auto_calculation_logic(control):
    assert control.compute_automated_target(-31) == 15
    assert control.compute_automated_target(-30) is None
    assert control.compute_automated_target(-29) == 20

    assert control.compute_automated_target(-26) == 20
    assert control.compute_automated_target(-25) is None
    assert control.compute_automated_target(-24) == 25

    assert control.compute_automated_target(-21) == 25
    assert control.compute_automated_target(-20) is None
    assert control.compute_automated_target(-19) == 30

    assert control.compute_automated_target(-16) == 30
    assert control.compute_automated_target(-15) is None
    assert control.compute_automated_target(-14) == 35

    assert control.compute_automated_target(-11) == 35
    assert control.compute_automated_target(-10) is None
    assert control.compute_automated_target(-9) == 40

    assert control.compute_automated_target(4) == 40
    assert control.compute_automated_target(5) is None
    assert control.compute_automated_target(6) == 45
    assert control.compute_automated_target(7) == 45


def test_auto_calculation_logic_with_negative_delta(control):
    settings.set("GENERAL.auto_delta", -2, persist=False)

    assert control.compute_automated_target(-31) == 15 - 2
    assert control.compute_automated_target(-30) is None
    assert control.compute_automated_target(-29) == 20 - 2

    assert control.compute_automated_target(-26) == 20 - 2
    assert control.compute_automated_target(-25) is None
    assert control.compute_automated_target(-24) == 25 - 2

    assert control.compute_automated_target(-21) == 25 - 2
    assert control.compute_automated_target(-20) is None
    assert control.compute_automated_target(-19) == 30 - 2

    assert control.compute_automated_target(-16) == 30 - 2
    assert control.compute_automated_target(-15) is None
    assert control.compute_automated_target(-14) == 35 - 2

    assert control.compute_automated_target(-11) == 35 - 2
    assert control.compute_automated_target(-10) is None
    assert control.compute_automated_target(-9) == 40 - 2

    assert control.compute_automated_target(4) == 40 - 2
    assert control.compute_automated_target(5) is None
    assert control.compute_automated_target(6) == 45 - 2
    assert control.compute_automated_target(7) == 45 - 2

    settings.set("GENERAL.auto_delta", 0, persist=False)


def test_auto_calculation_logic_with_positive_delta(control):
    settings.set("GENERAL.auto_delta", 2, persist=False)

    assert control.compute_automated_target(-31) == 15 + 2
    assert control.compute_automated_target(-30) is None
    assert control.compute_automated_target(-29) == 20 + 2

    assert control.compute_automated_target(-26) == 20 + 2
    assert control.compute_automated_target(-25) is None
    assert control.compute_automated_target(-24) == 25 + 2

    assert control.compute_automated_target(-21) == 25 + 2
    assert control.compute_automated_target(-20) is None
    assert control.compute_automated_target(-19) == 30 + 2

    assert control.compute_automated_target(-16) == 30 + 2
    assert control.compute_automated_target(-15) is None
    assert control.compute_automated_target(-14) == 35 + 2

    assert control.compute_automated_target(-11) == 35 + 2
    assert control.compute_automated_target(-10) is None
    assert control.compute_automated_target(-9) == 40 + 2

    assert control.compute_automated_target(4) == 40 + 2
    assert control.compute_automated_target(5) is None
    assert control.compute_automated_target(6) == 45 + 2
    assert control.compute_automated_target(7) == 45 + 2

    settings.set("GENERAL.auto_delta", 0, persist=False)


def test_auto_calculation_logic_with_missing_delta(control):
    settings.set("GENERAL.auto_delta", None, persist=False)

    assert control.compute_automated_target(-31) == 15

    settings.set("GENERAL.auto_delta", 0, persist=False)


def test_manual_high_humid_stopping(control, state_with_data):
    state_with_data["mode"] = tef_control.MODE.MANUAL
    state_with_data["state"] = tef_control.STATE.ON
    control.humidifier.turn_on()
    control.state = state_with_data
    control.state["humidity delay"] = 0
    settings.set("GENERAL.manual_target", 20, persist=False)
    assert control.humidifier_controller() == 2
    assert control.state["state"] == tef_control.STATE.OFF


def test_manual_high_keep_humid_off(control, state_with_data):
    state_with_data["mode"] = tef_control.MODE.MANUAL
    state_with_data["state"] = tef_control.STATE.OFF
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF


def test_manual_low_keep_humid_on(control, state_with_data):
    state_with_data["mode"] = tef_control.MODE.MANUAL
    state_with_data["state"] = tef_control.STATE.ON
    state_with_data["humidity"] = 20
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON


def test_manual_too_humid_starting(control, state_with_data):
    state_with_data["mode"] = tef_control.MODE.MANUAL
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 20
    settings.set("GENERAL.manual_target", 30, persist=False)
    control.humidifier.turn_off()
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON


def test_start_delay(control, state_with_data):
    settings.set("GENERAL.mode", "MANUAL", persist=False)
    settings.set("GENERAL.manual_target", 30, persist=False)

    state_with_data["state"] = tef_control.STATE.OFF
    control.humidifier.turn_off()

    state_with_data["humidity"] = 31
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF

    state_with_data["humidity"] = 30
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF

    control.state["humidity"] = 29
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF

    control.state["humidity"] = 28
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF

    control.state["humidity"] = 27
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON

    control.state["humidity"] = 26
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON


def test_stop_delay(control, state_with_data):
    settings.set("GENERAL.mode", "MANUAL", persist=False)
    settings.set("GENERAL.manual_target", 30, persist=False)

    state_with_data["state"] = tef_control.STATE.ON

    state_with_data["humidity"] = 29
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON

    control.state["humidity"] = 30
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON

    control.state["humidity"] = 31
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON

    control.state["humidity"] = 32
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON

    control.state["humidity"] = 33
    assert control.humidifier_controller() == 2
    assert control.state["state"] == tef_control.STATE.OFF

    control.state["humidity"] = 34
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF


def test_auto_high_humid_stopping(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = tef_control.STATE.ON
    state_with_data["humidity"] = 40
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 2
    assert control.state["state"] == tef_control.STATE.OFF


def test_auto_high_keep_humid_off(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 40
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF


def test_auto_low_humid_starting(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 20
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON


def test_auto_low_keep_humid_on(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = tef_control.STATE.ON
    state_with_data["humidity"] = 20
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON


def test_temp_delay_auto_start(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON

    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY
    control.state["state"] = tef_control.STATE.OFF
    assert control.humidifier_controller() == -4
    assert control.state["state"] == tef_control.STATE.ON
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_stay_on(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -5
    assert control.state["state"] == tef_control.STATE.ON
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_mode_stay_on(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -5
    assert control.state["state"] == tef_control.STATE.ON
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY

    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_stop_humid(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -5
    assert control.state["state"] == tef_control.STATE.ON
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY

    control.state["humidity"] = 50
    assert control.humidifier_controller() == 2
    assert control.state["state"] == tef_control.STATE.OFF
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_start_humid(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 50
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -5
    assert control.state["state"] == tef_control.STATE.OFF
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY

    control.state["humidity"] = 10
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_stop_humid_on_start(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["humidity"] = 50
    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -3
    assert control.state["state"] == tef_control.STATE.OFF
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_start_humid_on_start(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 50
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.OFF

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["humidity"] = 10
    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -4
    assert control.state["state"] == tef_control.STATE.ON
    assert control.state["mode"] == tef_control.MODE.TEMP_EMERGENCY


def test_weather_delay_manual(control, state_with_data):
    settings.set("GENERAL.mode", "MANUAL", persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON

    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY + 1000
    control.state["state"] = tef_control.STATE.OFF
    assert control.humidifier_controller() == 1
    assert control.state["state"] == tef_control.STATE.ON
    assert control.state["mode"] != tef_control.MODE.TEMP_EMERGENCY


def test_humidity_delay(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = tef_control.STATE.ON
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON

    control.state["humidity delay"] = tef_control.HUMIDITY_EMERGENCY_DELAY
    assert control.humidifier_controller() == -2
    assert control.state["state"] == tef_control.STATE.OFF
    assert control.state["mode"] == tef_control.MODE.NO_HUMIDITY


def test_humidity_and_temp_delay(control, state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = tef_control.STATE.ON
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == 0
    assert control.state["state"] == tef_control.STATE.ON

    control.state["humidity delay"] = tef_control.HUMIDITY_EMERGENCY_DELAY
    control.state["temp delay"] = tef_control.TEMP_EMERGENCY_DELAY + 1000
    assert control.humidifier_controller() == -2
    assert control.state["state"] == tef_control.STATE.OFF
    assert control.state["mode"] == tef_control.MODE.NO_HUMIDITY


def test_off_mode_from_on(control, state_with_data):
    settings.set("GENERAL.mode", "OFF", persist=False)
    state_with_data["state"] = tef_control.STATE.ON
    state_with_data["humidity"] = 10
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == -7
    assert control.state["state"] == tef_control.STATE.OFF


def test_off_mode_from_off(control, state_with_data):
    settings.set("GENERAL.mode", "OFF", persist=False)
    state_with_data["state"] = tef_control.STATE.OFF
    state_with_data["humidity"] = 50
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == -7
    assert control.state["state"] == tef_control.STATE.OFF


def test_dead_temp_band(control, state_with_data):
    state_with_data["target_humidity"] = 55
    state_with_data["target_temp"] = 5.5  # deadspot
    control.state = state_with_data
    control.humidifier_controller()
    control.state["target_humidity"] = 55


def test_dead_temp_band_int(control, state_with_data):
    state_with_data["target_humidity"] = 55
    state_with_data["target_temp"] = -10  # deadspot
    control.state = state_with_data
    control.humidifier_controller()
    control.state["target_humidity"] = 55


def test_valid_temp_change_humidity(control, state_with_data):
    state_with_data["target_humidity"] = 55
    state_with_data["target_temp"] = -5  # valid spot
    control.state = state_with_data
    control.humidifier_controller()
    control.state["target_humidity"] = 40


def test_is_active(control):
    assert control.is_active() == control.ecobee.is_active()


@patch("tefnut.control.control.TefnutController.data_collection_logic")
@patch("tefnut.control.control.get_temperature")
@patch("tefnut.control.ecobee.ecobee.get_humidity")
def test_working_loop(ecobee, get_temperature, data_collection_logic, control):
    ecobee.return_value = 35
    get_temperature.return_value = (5, 10, 15, 40)
    control.controler_loop()
    ecobee.assert_called_once()
    get_temperature.assert_called_once()
    data_collection_logic.assert_called_once()
    params = data_collection_logic.call_args[0][0]

    output = {
        "humidity": 35,
        "current_temp": 5,
        "future_temp": 10,
        "target_temp": 15,
        "outdoor_humidity": 40,
    }

    assert output.items() <= params.items()


@patch("tefnut.control.control.TefnutController.data_collection_logic")
@patch("tefnut.control.control.get_temperature")
@patch("tefnut.control.ecobee.ecobee.get_humidity")
def test_ecobee_timeout(ecobee, get_temperature, data_collection_logic, control):
    control.state["humidity time"] = time.time() + 60 * 60 * 60
    ecobee.return_value = 35
    get_temperature.return_value = (5, 10, 15, 40)
    control.controler_loop()
    assert not ecobee.called
    get_temperature.assert_called_once()
    data_collection_logic.assert_called_once()
    params = data_collection_logic.call_args[0][0]

    output = {
        "current_temp": 5,
        "future_temp": 10,
        "target_temp": 15,
        "outdoor_humidity": 40,
    }

    not_output = {"humidity": 35}

    assert output.items() <= params.items()
    assert not not_output.items() <= params.items()
    control.state["humidity time"] = time.time() - 60 * 60


@patch("tefnut.control.control.TefnutController.data_collection_logic")
@patch("tefnut.control.control.get_temperature")
@patch("tefnut.control.ecobee.ecobee.get_humidity")
def test_weather_timeout(ecobee, get_temperature, data_collection_logic, control):
    control.state["temp time"] = time.time() + 60 * 60 * 60
    ecobee.return_value = 35
    get_temperature.return_value = (5, 10, 15, 40)
    control.controler_loop()
    assert not get_temperature.called
    ecobee.assert_called_once()
    data_collection_logic.assert_called_once()
    params = data_collection_logic.call_args[0][0]

    output = {"humidity": 35}

    not_output = {
        "current_temp": 5,
        "future_temp": 10,
        "target_temp": 15,
        "outdoor_humidity": 40,
    }

    assert output.items() <= params.items()
    assert not not_output.items() <= params.items()
    control.state["temp time"] = time.time() - 60 * 60


@patch("tefnut.control.control.TefnutController.data_collection_logic")
@patch("tefnut.control.ecobee.ecobee.get_humidity")
def test_ecobee_Exception(ecobee, data_collection_logic, control, caplog):
    control.state["temp time"] = time.time() + 60 * 60 * 60
    ecobee.side_effect = Exception("test")

    control.controler_loop()

    assert "control main loop exception" in caplog.text
    assert not data_collection_logic.called


def test_goodbye(control, caplog):
    control.goodbye()
    assert "GOODBYE" in caplog.text
