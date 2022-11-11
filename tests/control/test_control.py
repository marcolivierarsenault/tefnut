import pytest
import time
import tefnut.control.control as control


@pytest.fixture
def state():
    return {'temp time': time.time() - control.DELAY_TEMP,
            'humidity time': time.time() - control.DELAY_HUMIDITY
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
    assert "current_temp" not in control.state

    current_values['future_temp'] = None
    control.data_collection_logic(current_values)
    assert "future_temp" not in control.state

    current_values['target_temp'] = None
    control.data_collection_logic(current_values)
    assert "target_temp" not in control.state

    del (current_values['current_temp'])
    control.data_collection_logic(current_values)
    assert "current_temp" not in control.state

    del (current_values['future_temp'])
    control.data_collection_logic(current_values)
    assert "future_temp" not in control.state

    del (current_values['target_temp'])
    control.data_collection_logic(current_values)
    assert "target_temp" not in control.state

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
    assert "humidity" not in control.state

    del (current_values['humidity'])
    control.data_collection_logic(current_values)
    assert "humidity" not in control.state

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
