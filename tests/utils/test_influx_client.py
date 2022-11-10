import pytest
from tefnut.utils.influx_client import InfluxClient
from influxdb_client import Point


@pytest.fixture
def influx_db():
    return InfluxClient()


@pytest.fixture
def point():
    return Point("measurement1").tag("tagname1", "tagvalue1").field("field1", 123)


def test_write_does_not_write_with_stub(influx_db, point):
    assert influx_db.write(point) == 1
