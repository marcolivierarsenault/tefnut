import pytest
import json
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


# response = client.post("/state", data={"mode": "MANUAL"}) # This throw an error