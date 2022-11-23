import pytest
import time
import tefnut.control.control as control
from tefnut.utils.setting import settings


@pytest.fixture
def state():
    return {'temp time': time.time() - control.DELAY_TEMP,
            'humidity time': time.time() - control.OFF_DELAY_HUMIDITY,
            'temp delay': 0,
            'humidity delay': 0,
            'current_temp': None,
            'future_temp': None,
            'target_temp': None,
            'humidity': None,
            'target_humidity': 40,
            'mode': control.MODE.AUTO,
            'state': control.STATE.OFF,
            }


@pytest.fixture
def state_with_data():
    return {'temp time': time.time() - control.DELAY_TEMP,
            'humidity time': time.time() - control.OFF_DELAY_HUMIDITY,
            'temp delay': 0,
            'humidity delay': 0,
            'current_temp': -20,
            'future_temp': -20,
            'target_temp': -20,
            'humidity': 40,
            'target_humidity': 30,
            'mode': control.MODE.AUTO,
            'state': control.STATE.OFF,
            }


@pytest.fixture
def current_values():
    return {'current_temp': 5,
            'future_temp': 6,
            'target_temp': 5.5,
            'finish time': time.time(),
            'start time': time.time()-1,
            'temp time': time.time()-0.5,
            'humidity time': time.time()-0.5,
            'temp delay': 7,
            'humidity delay': 7,
            'humidity': 45,
            }


def test_normal_beavior(current_values, state):
    control.state = state
    assert control.data_collection_logic(current_values) == 0


def test_none_temp_setting(current_values, state):
    control.state = state

    current_values['current_temp'] = None
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] is None
    assert control.humidifier_controller() == -1

    current_values['future_temp'] = None
    control.data_collection_logic(current_values)
    assert control.state["future_temp"] is None
    assert control.humidifier_controller() == -1

    current_values['target_temp'] = None
    control.data_collection_logic(current_values)
    assert control.state["target_temp"] is None
    assert control.humidifier_controller() == -1

    del (current_values['current_temp'])
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] is None
    assert control.humidifier_controller() == -1

    del (current_values['future_temp'])
    control.data_collection_logic(current_values)
    assert control.state["future_temp"] is None
    assert control.humidifier_controller() == -1

    del (current_values['target_temp'])
    control.data_collection_logic(current_values)
    assert control.state["target_temp"] is None
    assert control.humidifier_controller() == -1

    current_values['current_temp'] = 10
    current_values['future_temp'] = 11
    current_values['target_temp'] = 12
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12

    current_values['current_temp'] = None
    current_values['future_temp'] = None
    current_values['target_temp'] = None
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12

    del (current_values['current_temp'])
    del (current_values['future_temp'])
    del (current_values['target_temp'])
    control.data_collection_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12


def test_none_temp_time(current_values, state):
    control.state = state
    init_time = control.state['temp time']

    current_values['temp time'] = None
    control.data_collection_logic(current_values)
    assert init_time == control.state['temp time']

    del (current_values['temp time'])
    control.data_collection_logic(current_values)
    assert init_time == control.state['temp time']

    current_values['temp time'] = init_time+1
    control.data_collection_logic(current_values)
    assert init_time+1 == control.state['temp time']

    current_values['temp time'] = None
    control.data_collection_logic(current_values)
    assert init_time+1 == control.state['temp time']

    del (current_values['temp time'])
    control.data_collection_logic(current_values)
    assert init_time+1 == control.state['temp time']


def test_none_humidity_setting(current_values, state):
    control.state = state

    current_values['humidity'] = None
    control.data_collection_logic(current_values)
    assert control.state["humidity"] is None
    assert control.humidifier_controller() == -1

    del (current_values['humidity'])
    control.data_collection_logic(current_values)
    assert control.state["humidity"] is None
    assert control.humidifier_controller() == -1

    current_values['humidity'] = 10
    control.data_collection_logic(current_values)
    assert control.state["humidity"] == 10

    current_values['humidity'] = None
    control.data_collection_logic(current_values)
    assert control.state["humidity"] == 10

    del (current_values['humidity'])
    control.data_collection_logic(current_values)
    assert control.state["humidity"] == 10


def test_none_humidity_time(current_values, state):
    control.state = state
    init_time = control.state['humidity time']

    current_values['humidity time'] = None
    control.data_collection_logic(current_values)
    assert init_time == control.state['humidity time']

    del (current_values['humidity time'])
    control.data_collection_logic(current_values)
    assert init_time == control.state['humidity time']

    current_values['humidity time'] = init_time+1
    control.data_collection_logic(current_values)
    assert init_time+1 == control.state['humidity time']

    current_values['humidity time'] = None
    control.data_collection_logic(current_values)
    assert init_time+1 == control.state['humidity time']

    del (current_values['humidity time'])
    control.data_collection_logic(current_values)
    assert init_time+1 == control.state['humidity time']


def test_auto_calculation_logic():
    assert control.compute_automated_target(-31) == 15
    assert control.compute_automated_target(-30) == 15
    assert control.compute_automated_target(-29) == 20

    assert control.compute_automated_target(-26) == 20
    assert control.compute_automated_target(-25) == 20
    assert control.compute_automated_target(-24) == 25

    assert control.compute_automated_target(-21) == 25
    assert control.compute_automated_target(-20) == 25
    assert control.compute_automated_target(-19) == 30

    assert control.compute_automated_target(-16) == 30
    assert control.compute_automated_target(-15) == 30
    assert control.compute_automated_target(-14) == 35

    assert control.compute_automated_target(-11) == 35
    assert control.compute_automated_target(-10) == 35
    assert control.compute_automated_target(-9) == 40

    assert control.compute_automated_target(4) == 40
    assert control.compute_automated_target(5) == 40
    assert control.compute_automated_target(6) == 45
    assert control.compute_automated_target(7) == 45


def test_manual_high_humid_stopping(state_with_data):
    state_with_data["mode"] = control.MODE.MANUAL
    state_with_data["state"] = control.STATE.ON
    control.humidifier.turn_on()
    control.state = state_with_data
    control.state['humidity delay'] = 0
    settings.set("GENERAL.manual_target", 20, persist=False)
    assert control.humidifier_controller() == 2
    assert control.state["state"] == control.STATE.OFF


def test_manual_high_keep_humid_off(state_with_data):
    state_with_data["mode"] = control.MODE.MANUAL
    state_with_data["state"] = control.STATE.OFF
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF


def test_manual_low_keep_humid_on(state_with_data):
    state_with_data["mode"] = control.MODE.MANUAL
    state_with_data["state"] = control.STATE.ON
    state_with_data["humidity"] = 20
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON


def test_manual_too_humid_starting(state_with_data):
    state_with_data["mode"] = control.MODE.MANUAL
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 20
    settings.set("GENERAL.manual_target", 30, persist=False)
    control.humidifier.turn_off()
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON


def test_start_delay(state_with_data):
    settings.set("GENERAL.mode", "MANUAL", persist=False)
    settings.set("GENERAL.manual_target", 30, persist=False)

    state_with_data["state"] = control.STATE.OFF
    control.humidifier.turn_off()

    state_with_data["humidity"] = 31
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF

    state_with_data["humidity"] = 30
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF

    control.state["humidity"] = 29
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF

    control.state["humidity"] = 28
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF

    control.state["humidity"] = 27
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON

    control.state["humidity"] = 26
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON


def test_stop_delay(state_with_data):
    settings.set("GENERAL.mode", "MANUAL", persist=False)
    settings.set("GENERAL.manual_target", 30, persist=False)

    state_with_data["state"] = control.STATE.ON

    state_with_data["humidity"] = 29
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON

    control.state["humidity"] = 30
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON

    control.state["humidity"] = 31
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON

    control.state["humidity"] = 32
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON

    control.state["humidity"] = 33
    assert control.humidifier_controller() == 2
    assert control.state["state"] == control.STATE.OFF

    control.state["humidity"] = 34
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF


def test_auto_high_humid_stopping(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = control.STATE.ON
    state_with_data["humidity"] = 40
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 2
    assert control.state["state"] == control.STATE.OFF


def test_auto_high_keep_humid_off(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 40
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF


def test_auto_low_humid_starting(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 20
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON


def test_auto_low_keep_humid_on(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = control.STATE.ON
    state_with_data["humidity"] = 20
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON


def test_temp_delay_auto_start(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON

    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY
    control.state["state"] = control.STATE.OFF
    assert control.humidifier_controller() == -4
    assert control.state["state"] == control.STATE.ON
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_stay_on(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -5
    assert control.state["state"] == control.STATE.ON
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_mode_stay_on(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -5
    assert control.state["state"] == control.STATE.ON
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY

    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_stop_humid(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -5
    assert control.state["state"] == control.STATE.ON
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY

    control.state["humidity"] = 50
    assert control.humidifier_controller() == 2
    assert control.state["state"] == control.STATE.OFF
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_start_humid(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 50
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -5
    assert control.state["state"] == control.STATE.OFF
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY

    control.state["humidity"] = 10
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_stop_humid_on_start(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["humidity"] = 50
    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -3
    assert control.state["state"] == control.STATE.OFF
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY


def test_temp_delay_auto_start_humid_on_start(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    settings.set("GENERAL.emergency_target", 30, persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 50
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.OFF

    settings.set("GENERAL.mode", "AUTO", persist=False)
    control.state["humidity"] = 10
    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY
    assert control.humidifier_controller() == -4
    assert control.state["state"] == control.STATE.ON
    assert control.state["mode"] == control.MODE.TEMP_EMERGENCY


def test_weather_delay_manual(state_with_data):
    settings.set("GENERAL.mode", "MANUAL", persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON

    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY+1000
    control.state["state"] = control.STATE.OFF
    assert control.humidifier_controller() == 1
    assert control.state["state"] == control.STATE.ON
    assert control.state["mode"] != control.MODE.TEMP_EMERGENCY


def test_humidity_delay(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = control.STATE.ON
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON

    control.state["humidity delay"] = control.HUMIDITY_EMERGENCY_DELAY
    assert control.humidifier_controller() == -2
    assert control.state["state"] == control.STATE.OFF
    assert control.state["mode"] == control.MODE.NO_HUMIDITY


def test_humidity_and_temp_delay(state_with_data):
    settings.set("GENERAL.mode", "AUTO", persist=False)
    state_with_data["state"] = control.STATE.ON
    state_with_data["humidity"] = 10
    state_with_data["target_temp"] = -15
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == 0
    assert control.state["state"] == control.STATE.ON

    control.state["humidity delay"] = control.HUMIDITY_EMERGENCY_DELAY
    control.state["temp delay"] = control.TEMP_EMERGENCY_DELAY+1000
    assert control.humidifier_controller() == -2
    assert control.state["state"] == control.STATE.OFF
    assert control.state["mode"] == control.MODE.NO_HUMIDITY


def test_off_mode_from_on(state_with_data):
    settings.set("GENERAL.mode", "OFF", persist=False)
    state_with_data["state"] = control.STATE.ON
    state_with_data["humidity"] = 10
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == -7
    assert control.state["state"] == control.STATE.OFF


def test_off_mode_from_off(state_with_data):
    settings.set("GENERAL.mode", "OFF", persist=False)
    state_with_data["state"] = control.STATE.OFF
    state_with_data["humidity"] = 50
    control.state = state_with_data
    control.humidifier.turn_on()
    assert control.humidifier_controller() == -7
    assert control.state["state"] == control.STATE.OFF
