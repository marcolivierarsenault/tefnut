from unittest.mock import patch

import pytest
from influxdb_client import Point

from tefnut.utils.influx_client import InfluxClient
from tefnut.utils.setting import settings


@pytest.fixture
def influx_db():
    return InfluxClient()


@pytest.fixture
def working_influx_db():
    settings.set("INFLUX.enable", True, persist=False)
    return InfluxClient()


@pytest.fixture
def point():
    return Point("measurement1").tag("tagname1", "tagvalue1").field("field1", 123)


def test_write_does_not_write_with_stub(influx_db, point):
    assert influx_db.write(point) == 1


def test_influx_connection_test_write(working_influx_db, point):
    with patch("influxdb_client.client.write_api.WriteApi.write") as write_api:
        assert working_influx_db.write(point) == 0
        write_api.assert_called_once()


def test_influx_connection_raise_exeption_without_mock(
    working_influx_db, point, caplog
):
    with patch("influxdb_client.client.write_api.WriteApi.write") as write_api:
        write_api.side_effect = Exception("test")
        assert working_influx_db.write(point) == -1
        write_api.assert_called_once()
        assert "Faillure to configure Influx DB client" in caplog.text


def test_influx_failing_to_create_client(caplog):
    settings.set("INFLUX.enable", True, persist=False)
    with patch(
        "influxdb_client.client.influxdb_client.InfluxDBClient.__init__"
    ) as influx_client_mock:
        influx_client_mock.side_effect = Exception("test")
        InfluxClient()
        influx_client_mock.assert_called_once()
        assert "Faillure to configure Influx DB client" in caplog.text
