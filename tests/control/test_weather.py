import time
from tefnut.control.weather import get_temperature, calculate_target
from tefnut.utils.setting import settings


api_key = settings.get("WEATHER.api_key")
lat = settings.get("WEATHER.lat")
lon = settings.get("WEATHER.lon")

current_temp_url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)
future_temp_url = "https://api.openweathermap.org/data/2.5/forecast?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api_key)


def test_target_calculation():
    assert calculate_target(-10, -10) == -10
    assert calculate_target(-10, -5) == -10
    assert calculate_target(-10, -20) == -15
    assert calculate_target(-10, 0) == -10
    assert calculate_target(-10, -11) == -10.5


def test_valide_returns_from_url(requests_mock):
    requests_mock.get(current_temp_url, json={"main": {"temp": 10}})
    requests_mock.get(future_temp_url, json={"list": [{"dt": int(time.time())+60*60*2, "main": {"temp": 20}}]})
    assert get_temperature() == (10, 20, 10)


def test_valide_returns_from_url_second_forecast(requests_mock):
    requests_mock.get(current_temp_url, json={"main": {"temp": 10}})
    requests_mock.get(future_temp_url, json={"list": [{"dt": 1669075200+60*10, "main": {"temp": 20}},
                                                      {"dt": 1669086000+60*60*4, "main": {"temp": 40}}]})
    assert get_temperature() == (10, 40, 10)


def test_url_one_wrong_API(requests_mock):
    requests_mock.get(current_temp_url, status_code=401)
    assert get_temperature() == (None, None, None)


def test_url_two_wrong_API(requests_mock):
    requests_mock.get(current_temp_url, json={"main": {"temp": 10}})
    requests_mock.get(future_temp_url, status_code=401)
    assert get_temperature() == (None, None, None)


def test_unexpected_answer(requests_mock):
    requests_mock.get(current_temp_url, json={"main": {"temp": 10}})
    requests_mock.get(future_temp_url, json={"notList": [{"main": {"temp": 20}}]})
    assert get_temperature() == (None, None, None)


def test_none_json_answer(requests_mock):
    requests_mock.get(current_temp_url, text="test")
    requests_mock.get(future_temp_url, text="test")
    assert get_temperature() == (None, None, None)
