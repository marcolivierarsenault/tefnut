import pytest
import json
import tefnut.webui.webservice as webservice
from tefnut.control.control import state
from tefnut.utils.constant import STATE, MODE
from tefnut.utils.setting import settings


@pytest.fixture(scope="module", autouse=True)
def configure_state():
    print("--------------------")


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
        state == json.loads(response.data)

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
        state['mode'] = MODE.AUTO
        settings.set("GENERAL.mode", MODE.AUTO.name, persist=False)

        response = client.post("/state", data="{\"mode\": \"MANUAL\"}")
        assert json.loads(response.data)["mode"] != "MANUAL"
        assert state['mode'] != MODE.MANUAL


# response = client.post("/state", data={"mode": "MANUAL"}) # This throw an error