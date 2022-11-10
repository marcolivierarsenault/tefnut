import pytest
import time
import tefnut.control.control as control


@pytest.fixture
def state():
    return {'temp time': time.time() - control.DELAY_TEMP}


@pytest.fixture
def current_values():
    return {'current_temp': 5,
            'future_temp': 6,
            'target_temp': 5.5,
            'finish time': time.time(),
            'start time': time.time()-1,
            'temp time': time.time()-0.5,
            'temp delay': 7,
            }


def test_normal_beavior(current_values, state):
    control.state = state
    assert control.humidificator_logic(current_values) == 0


def test_none_temp_setting(current_values, state):
    control.state = state

    current_values['current_temp'] = None
    control.humidificator_logic(current_values)
    assert "current_temp" not in control.state

    current_values['future_temp'] = None
    control.humidificator_logic(current_values)
    assert "future_temp" not in control.state

    current_values['target_temp'] = None
    control.humidificator_logic(current_values)
    assert "target_temp" not in control.state

    del (current_values['current_temp'])
    control.humidificator_logic(current_values)
    assert "current_temp" not in control.state

    del (current_values['future_temp'])
    control.humidificator_logic(current_values)
    assert "future_temp" not in control.state

    del (current_values['target_temp'])
    control.humidificator_logic(current_values)
    assert "target_temp" not in control.state

    current_values['current_temp'] = 10
    current_values['future_temp'] = 11
    current_values['target_temp'] = 12
    control.humidificator_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12

    current_values['current_temp'] = None
    current_values['future_temp'] = None
    current_values['target_temp'] = None
    control.humidificator_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12

    del (current_values['current_temp'])
    del (current_values['future_temp'])
    del (current_values['target_temp'])
    control.humidificator_logic(current_values)
    assert control.state["current_temp"] == 10
    assert control.state["future_temp"] == 11
    assert control.state["target_temp"] == 12


def test_none_temp_time(current_values, state):
    control.state = state
    init_time = control.state['temp time']

    current_values['temp time'] = None
    control.humidificator_logic(current_values)
    assert init_time == control.state['temp time']

    del (current_values['temp time'])
    control.humidificator_logic(current_values)
    assert init_time == control.state['temp time']

    current_values['temp time'] = init_time+1
    control.humidificator_logic(current_values)
    assert init_time+1 == control.state['temp time']

    current_values['temp time'] = None
    control.humidificator_logic(current_values)
    assert init_time+1 == control.state['temp time']

    del (current_values['temp time'])
    control.humidificator_logic(current_values)
    assert init_time+1 == control.state['temp time']
