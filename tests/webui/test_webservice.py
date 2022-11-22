import pytest
import json
from tefnut.webui.webservice import app as o_app
from tefnut.control.control import state


@pytest.fixture()
def app():
    app = o_app
    app.config.update({
        "TESTING": True,
        "LOGIN_DISABLED": True
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


def test_request_example(client):
    response = client.get("/")
    print(response)
    assert b"Status" in response.data


def test_get_state(client):
    response = client.post("/state")
    state == json.loads(response.data)
