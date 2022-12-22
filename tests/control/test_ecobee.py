import tefnut.control.ecobee as ecobee
import os
import pytz
import requests_mock
import requests
from datetime import datetime
from unittest.mock import patch
from tests.common import load_fixture


class TestWorkingEcobee:

    def setup_class(cls):
        with requests_mock.Mocker() as m:
            m.get("https://api.ecobee.com/authorize?client_id=dsaDwe34fDsfedsssd3dasADWDqwdawd&"
                  "response_type=ecobeePin&scope=smartWrite",
                  text=load_fixture("tests/control/fixture/auth.json")
                  )
            m.post("https://api.ecobee.com/token?client_id=dsaDwe34fDsfedsssd3dasADWDqwdawd"
                   "&code=1234-5678&grant_type=ecobeePin",
                   text=load_fixture("tests/control/fixture/token.json")
                   )

            cls.ecobee = ecobee.ecobee("test")

    def teardown_class(cls):
        os.remove("test")

    def test_getting_humidity(self, requests_mock):
        requests_mock.get('https://api.ecobee.com/1/thermostat',
                          text=load_fixture("tests/control/fixture/thermostat.json"))
        assert self.ecobee.get_humidity() == 39

    def test_pin(self):
        assert self.ecobee.get_pin() == "ABCD-EFGH"

    def test_get_humidity_timeout(self, requests_mock, caplog):
        requests_mock.get('https://api.ecobee.com/1/thermostat', exc=requests.exceptions.ConnectTimeout)
        assert self.ecobee.get_humidity() is None
        assert 'Failed to retreive humidity' in caplog.text


class TestOtherFlowEcobee:

    def test_refresh_token_expires_on(self, mocker):

        with requests_mock.Mocker() as m:
            m.get("https://api.ecobee.com/authorize?client_id=dsaDwe34fDsfedsssd3dasADWDqwdawd&"
                  "response_type=ecobeePin&scope=smartWrite",
                  text=load_fixture("tests/control/fixture/auth.json")
                  )
            m.post("https://api.ecobee.com/token?client_id=dsaDwe34fDsfedsssd3dasADWDqwdawd"
                   "&code=1234-5678&grant_type=ecobeePin",
                   text=load_fixture("tests/control/fixture/token.json")
                   )

            local_ecobee = ecobee.ecobee("test")

        now = datetime.now(pytz.utc)
        assert local_ecobee.ecobee_service.refresh_token_expires_on != now
        local_ecobee.ecobee_service.refresh_token_expires_on = now
        assert local_ecobee.ecobee_service.refresh_token_expires_on == now

        with patch(
            "tefnut.control.ecobee.ecobee.authorize"
        ) as authorize:

            with patch(
                "tefnut.control.ecobee.ecobee.request_tokens"
            ) as request_tokens:

                local_ecobee.update_token()
                authorize.assert_called_once()
                request_tokens.assert_called_once()

        os.remove("test")

    def test_access_token_expires_on(self, mocker):

        with requests_mock.Mocker() as m:
            m.get("https://api.ecobee.com/authorize?client_id=dsaDwe34fDsfedsssd3dasADWDqwdawd&"
                  "response_type=ecobeePin&scope=smartWrite",
                  text=load_fixture("tests/control/fixture/auth.json")
                  )
            m.post("https://api.ecobee.com/token?client_id=dsaDwe34fDsfedsssd3dasADWDqwdawd"
                   "&code=1234-5678&grant_type=ecobeePin",
                   text=load_fixture("tests/control/fixture/token.json")
                   )

            local_ecobee = ecobee.ecobee("test")

        now = datetime.now(pytz.utc)
        assert local_ecobee.ecobee_service.access_token_expires_on != now
        local_ecobee.ecobee_service.access_token_expires_on = now
        assert local_ecobee.ecobee_service.access_token_expires_on == now

        with patch(
            "pyecobee.EcobeeService.refresh_tokens"
        ) as refresh_tokens:

            local_ecobee.update_token()
            refresh_tokens.assert_called_once()

        os.remove("test")

