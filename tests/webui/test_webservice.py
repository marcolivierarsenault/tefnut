import pytest
import json
import copy
import time
import tefnut.webui.webservice as webservice
import tefnut.control.control as control
from tefnut.utils.constant import STATE, MODE
from tefnut.utils.setting import settings


@pytest.fixture(scope="module", autouse=True)
def configure_state():
    control.state["current_temp"] = 10
    control.state["future_temp"] = 20
    control.state["target_temp"] = 30
    control.state["humidity"] = 10
    control.state["temp time"] = time.time()
    control.state["humidity time"] = time.time()


@pytest.fixture()
def app():
    app = webservice.app
    app.config.update({
        "TESTING": True,
        "LOGIN_DISABLED": True
    })

    webservice.persist = False

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


class TestWebserviceReturn:

    def test_get_status(self, client):
        response = client.get("/")
        assert b"Status" in response.data

    def test_post_get_state(self, client):
        response = client.post("/state")
        assert control.state == json.loads(response.data)

    def test_get_login_page(self, client):
        response = client.get("/login")
        assert b"Login" in response.data

    def test_get_logout_page(self, client):
        response = client.get("/logout")
        assert b"Redirecting" in response.data

    def test_invalid_page_throw_404(self, client):
        response = client.get("/dsadas")
        assert b"Invalid page" in response.data
        assert response.status == "404 NOT FOUND"


class TestChangeState:

    def test_post_get_state_change_mode_auto_to_manual(self, client):
        control.state['mode'] = MODE.AUTO
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] == "MANUAL"
        assert control.state['mode'] == MODE.MANUAL

    def test_post_get_state_change_mode_auto_to_manual_start_hum(self, client):
        control.state['mode'] = MODE.AUTO
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)
        settings.set("GENERAL.manual_target", 30, persist=False)
        control.state['humidity'] = 10

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] == "MANUAL"
        assert control.state['mode'] == MODE.MANUAL
        assert control.state['state'] == STATE.ON

    def test_post_get_state_change_mode_auto_to_manual_stop_hum(self, client):
        control.state['mode'] = MODE.AUTO
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)
        settings.set("GENERAL.manual_target", 30, persist=False)
        control.state['humidity'] = 50

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] == "MANUAL"
        assert control.state['mode'] == MODE.MANUAL
        assert control.state['state'] == STATE.OFF

    def test_cannot_bypass_alarms_temp_manual(self, client):
        control.state['mode'] = MODE.MANUAL
        control.state["temp delay"] = 100000000

        response = client.post("/state", data="{\"mode\": \"AUTO\"}")
        assert json.loads(response.data)["mode"] == "TEMP_EMERGENCY"
        assert control.state['mode'] == MODE.TEMP_EMERGENCY
        assert control.state['state'] == STATE.ON

    def test_cannot_bypass_alarms_humidity_manual(self, client):
        control.state['mode'] = MODE.OFF
        control.state["humidity delay"] = 100000000

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] == "NO_HUMIDITY"
        assert control.state['mode'] == MODE.NO_HUMIDITY
        assert control.state['state'] == STATE.OFF

    def test_cannot_bypass_alarms_humidity_auto(self, client):
        control.state['mode'] = MODE.OFF
        control.state["humidity delay"] = 100000000

        response = client.post("/state", data="{\"mode\": \"AUTO\"}")
        assert json.loads(response.data)["mode"] == "NO_HUMIDITY"
        assert control.state['mode'] == MODE.NO_HUMIDITY
        assert control.state['state'] == STATE.OFF

    def test_setting_manual_target(self, client):
        control.state['mode'] = MODE.MANUAL
        control.state["humidity delay"] = 10
        control.state["humidity"] = 20
        control.state['mode'] = MODE.OFF

        response = client.post("/state", data="{\"manual_target\": 32}")
        assert json.loads(response.data)["mode"] == "MANUAL"
        assert json.loads(response.data)["target_humidity"] == 32
        assert json.loads(response.data)["state"] == "ON"

        assert control.state["target_humidity"] == 32
        assert control.state['state'] == STATE.ON

    def test_invalid_mode(self, client, caplog):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"mode\": \"adasdad\"}")
        assert ["Error incoming data, mode invalid: adasdad"] == [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_data(self, client, caplog):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="fsdfsdf")
        assert "Error opening json" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_manual_target_data(self, client, caplog):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"manual_target\": \"adasdad\"}")
        assert "Error incoming data, manual_target invalid: adasdad" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_too_low_target(self, client, caplog):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"manual_target\": 2}")
        assert "Error incoming data, manual_target is out of range: 2" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_too_high_target(self, client, caplog):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"manual_target\": 52}")
        assert "Error incoming data, manual_target is out of range: 52" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_dict_key(self, client, caplog):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"manual_tss\": 52}")
        assert "Error incoming data, invalid data: {'manual_tss': 52}" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state
