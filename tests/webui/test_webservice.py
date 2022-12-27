import pytest
import json
import copy
import time
import base64
from unittest.mock import patch
import tefnut.webui.webservice as webservice
import tefnut.control.control as ctl
from tefnut.utils.constant import STATE, MODE
from tefnut.utils.setting import settings


@pytest.fixture()
def control():
    control = ctl.TefnutController()
    control.state["current_temp"] = 10
    control.state["future_temp"] = 20
    control.state["target_temp"] = 30
    control.state["humidity"] = 10
    control.state["temp time"] = time.time()
    control.state["humidity time"] = time.time()
    control.state["auto_delta"] = 0
    control.state["humidity delay"] = 0
    control.state["temp delay"] = 0
    return control


@pytest.fixture()
def app(control):
    app = webservice.app
    app.config.update({
        "TESTING": True,
        "LOGIN_DISABLED": True
    })

    webservice.sha = "123"
    webservice.version = "1.2.3"

    webservice.persist = False

    webservice.tefnut_controller = control

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def app_nl():
    app = webservice.app
    app.config.update({
        "TESTING": True,
    })

    webservice.sha = "123"
    webservice.version = "1.2.3"

    webservice.persist = False

    yield app


@pytest.fixture()
def client_nl(app_nl):
    return app_nl.test_client()


class TestLogin:

    def test_no_login_get_redirected(self, client_nl):
        response = client_nl.get("/")
        assert b"Humidifier Mode" not in response.data

    def test_login_http_get_redirected(self, client_nl):
        credentials = base64.b64encode(b"test:test").decode('utf-8')
        response = client_nl.get("/", headers={"Authorization": "Basic {}".format(credentials)})
        assert b"Humidifier Mode" in response.data

    def test_login_http_invalid(self, client_nl):
        credentials = base64.b64encode(b"test:test2").decode('utf-8')
        response = client_nl.get("/", headers={"Authorization": "Basic {}".format(credentials)})
        assert response.status == "302 FOUND"

    def test_form_login(self, client_nl):
        response = client_nl.post('/login', data=dict(username='test', password='test'), follow_redirects=True)
        assert b"Humidifier Mode" in response.data

    def test_form_login_failed_auth(self, client_nl):
        response = client_nl.post('/login', data=dict(username='testworing', password='testworing'), follow_redirects=True)
        assert b"Humidifier Mode" not in response.data


class TestWebserviceReturn:

    def test_get_status(self, client):
        response = client.get("/")
        assert b"Status" in response.data

    def test_post_get_state(self, client):
        response = client.post("/state")
        control = webservice.tefnut_controller
        assert control.state == json.loads(response.data)

    def test_get_login_page(self, client):
        response = client.get("/login")
        assert b"Login" in response.data

    def test_get_logout_page(self, client):
        response = client.get("/logout")
        assert b"Redirecting" in response.data

    def test_get_version(self, client):
        response = client.get("/version")
        assert b'{"sha":"123","version":"1.2.3"}' in response.data

    def test_invalid_page_throw_404(self, client):
        response = client.get("/dsadas")
        assert b"Invalid page" in response.data
        assert response.status == "404 NOT FOUND"

    def test_invalid_page_throw_500(self, client):
        with patch("tefnut.webui.webservice.User") as mocked_template:
            mocked_template.side_effect = Exception("test")
            response = client.post("/login")
            assert response.status == "500 INTERNAL SERVER ERROR"


class TestChangeState:

    def test_post_get_state_change_mode_auto_to_manual(self, client, control):
        control.state['mode'] = MODE.AUTO
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] == "MANUAL"
        assert control.state['mode'] == MODE.MANUAL

    def test_post_get_state_change_mode_auto_to_manual_start_hum(self, client, control):
        control.state['mode'] = MODE.AUTO
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)
        settings.set("GENERAL.manual_target", 30, persist=False)
        control.state['humidity'] = 10

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] == "MANUAL"
        assert control.state['mode'] == MODE.MANUAL
        assert control.state['state'] == STATE.ON

    def test_post_get_state_change_mode_auto_to_manual_stop_hum(self, client, control):
        control.state['mode'] = MODE.AUTO
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)
        settings.set("GENERAL.manual_target", 30, persist=False)
        control.state['humidity'] = 50

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] == "MANUAL"
        assert control.state['mode'] == MODE.MANUAL
        assert control.state['state'] == STATE.OFF

    def test_cannot_bypass_alarms_temp_manual(self, client, control):
        control.state['mode'] = MODE.MANUAL
        control.state["temp delay"] = 100000000

        response = client.post("/state", data="{\"mode\": \"AUTO\"}")
        assert json.loads(response.data)["mode"] == "TEMP_EMERGENCY"
        assert control.state['mode'] == MODE.TEMP_EMERGENCY

    def test_cannot_bypass_alarms_humidity_manual(self, client, control):
        control.state['mode'] = MODE.OFF
        control.state["humidity delay"] = 100000000

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] == "NO_HUMIDITY"
        assert control.state['mode'] == MODE.NO_HUMIDITY
        assert control.state['state'] == STATE.OFF

    def test_cannot_bypass_alarms_humidity_auto(self, client, control):
        control.state['mode'] = MODE.OFF
        control.state["humidity delay"] = 100000000

        response = client.post("/state", data="{\"mode\": \"AUTO\"}")
        assert json.loads(response.data)["mode"] == "NO_HUMIDITY"
        assert control.state['mode'] == MODE.NO_HUMIDITY
        assert control.state['state'] == STATE.OFF

    def test_setting_manual_target(self, client, control):
        control.state['mode'] = MODE.MANUAL
        control.state["humidity delay"] = 10
        control.state["temp delay"] = 10
        control.state["humidity"] = 20
        settings.set("GENERAL.mode", MODE.MANUAL.name, persist=False)
        control.state['mode'] = MODE.OFF

        response = client.post("/state", data="{\"manual_target\": 32}")
        assert json.loads(response.data)["mode"] == "MANUAL"
        assert json.loads(response.data)["target_humidity"] == 32
        assert json.loads(response.data)["state"] == "ON"

        assert control.state["target_humidity"] == 32
        assert control.state['state'] == STATE.ON

    def test_invalid_mode(self, client, caplog, control):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"mode\": \"adasdad\"}")
        assert ["Error incoming data, mode invalid: adasdad"] == [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_data(self, client, caplog, control):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="fsdfsdf")
        assert "Error opening json" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_manual_target_data(self, client, caplog, control):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"manual_target\": \"adasdad\"}")
        assert "Error incoming data, manual_target invalid: adasdad" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_too_low_target(self, client, caplog, control):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"manual_target\": 2}")
        assert "Error incoming data, manual_target is out of range: 2" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_too_high_target(self, client, caplog, control):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"manual_target\": 52}")
        assert "Error incoming data, manual_target is out of range: 52" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_invalid_dict_key(self, client, caplog, control):
        copy_state = copy.deepcopy(control.state)
        response = client.post("/state", data="{\"manual_tss\": 52}")
        assert "Error incoming data, invalid data: {'manual_tss': 52}" in [rec.message for rec in caplog.records]
        assert json.loads(response.data) == copy_state

    def test_setting_auto_delta(self, client, control):
        control.state['mode'] = MODE.AUTO
        control.state["humidity delay"] = 10
        control.state["temp delay"] = 10
        control.state["humidity"] = 20
        control.state["auto_delta"] = -2
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)
        control.state['mode'] = MODE.OFF

        response = client.post("/state", data="{\"auto_delta\": 0}")
        assert json.loads(response.data)["auto_delta"] == 0

    def test_setting_auto_delta_invalid_range(self, client, caplog, control):
        control.state['mode'] = MODE.AUTO
        control.state["humidity delay"] = 10
        control.state["temp delay"] = 10
        control.state["humidity"] = 20
        control.state["auto_delta"] = -2
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)
        control.state['mode'] = MODE.OFF

        response = client.post("/state", data="{\"auto_delta\": -30}")
        assert json.loads(response.data)["auto_delta"] == -2
        assert "Error incoming data, auto_delta is out of range: -30" in [rec.message for rec in caplog.records]

    def test_setting_auto_delta_invalid_type(self, client, caplog, control):
        control.state['mode'] = MODE.AUTO
        control.state["humidity delay"] = 10
        control.state["temp delay"] = 10
        control.state["humidity"] = 20
        control.state["auto_delta"] = -2
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)
        control.state['mode'] = MODE.OFF

        response = client.post("/state", data="{\"auto_delta\": \"0\"}")
        assert json.loads(response.data)["auto_delta"] == -2
        assert "Error incoming data, auto_delta invalid: 0" in [rec.message for rec in caplog.records]


class TestFramework:
    def test_shutdown(self, app, caplog):
        webservice.close_tefnut()
        assert 'Stopping tefnut' in caplog.text
        assert 'GOODBYE' in caplog.text

    def test_background_job_gets_added(app):
        assert len(webservice.scheduler.get_jobs()) == 1
        assert webservice.scheduler.get_jobs()[0].id == 'tefnut_update'

    @patch('tefnut.webui.webservice.tefnut_controller.controler_loop')
    def test_background_job_loads_controller(self, tefnut_controller, app):
        webservice.background_job()
        tefnut_controller.assert_called_once()

    @patch('tefnut.webui.webservice.atexit.register')
    @patch('tefnut.webui.webservice.control.TefnutController')
    def test_loading_job(self, atexit, tefnut_controller, app):
        webservice.load_application()
        atexit.assert_called_once()
        tefnut_controller.assert_called_once()
        assert webservice.sha != ""
        assert webservice.version != ""
        assert webservice.tefnut_controller is not None


