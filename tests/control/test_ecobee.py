import tefnut.control.ecobee as ecobee
import os
import requests_mock


class TestWorkingEcobee:

    def setup_class(cls):
        MOCK_DATA_AUTH = "{\"ecobeePin\":\"ABCD-EFGH\",\"code\":\"1234-5678\",\"interval\":5,\"expires_in\":900,\"scope\":\"" \
            "openid,offline_access,smartWrite\"}"
        MOCK_DATA_TOKEN = "{\"access_token\":\"Rc7JE8P7XUgSCPogLOx2VLMfITqQQrjg\",\"token_type\":\"Bearer\",\"expires_in" \
            "\":3599,\"refresh_token\":\"og2Obost3ucRo1ofo0EDoslGltmFMe2g\",\"scope\":\"smartWrite\"}"
        with requests_mock.Mocker() as m:
            m.get(
                "https://api.ecobee.com/authorize?client_id=yDhMpHOSKzDPyDbaIXQZYPLUcfhgHrge&response_type=ecobeePin&scope=smartWrite",
                    text=MOCK_DATA_AUTH,
                )
            m.post("https://api.ecobee.com/token?client_id=yDhMpHOSKzDPyDbaIXQZYPLUcfhgHrge&code=1234-5678&grant_type=ecobeePin", 
                   text=MOCK_DATA_TOKEN
                   )

            cls.ecobee = ecobee.ecobee("test")

    def teardown_class(cls):
        os.remove("test")

    def test_getting_humidity(self, requests_mock):
        requests_mock.get('https://api.ecobee.com/1/thermostat', text="{\"page\":{\"page\":1,\"totalPages\":1,\"pageSize\":1,\"total\":1},\"thermostatList\":[{\"identifier\":\"522674392583\",\"name\":\"Myecobee\",\"thermostatRev\":\"221220232727\",\"isRegistered\":true,\"modelNumber\":\"vulcanSmart\",\"brand\":\"ecobee\",\"features\":\"Home,HomeKit\",\"lastModified\":\"2022-12-2023:27:27\",\"thermostatTime\":\"2022-12-2120:13:18\",\"utcTime\":\"2022-12-2201:13:18\",\"runtime\":{\"runtimeRev\":\"221222011246\",\"connected\":true,\"firstConnected\":\"2021-10-0502:18:34\",\"connectDateTime\":\"2022-12-2012:01:01\",\"disconnectDateTime\":\"2022-12-0901:54:00\",\"lastModified\":\"2022-12-2201:12:46\",\"lastStatusModified\":\"2022-12-2201:12:46\",\"runtimeDate\":\"2022-12-22\",\"runtimeInterval\":12,\"actualTemperature\":687,\"actualHumidity\":39,\"rawTemperature\":687,\"showIconMode\":0,\"desiredHeat\":680,\"desiredCool\":716,\"desiredHumidity\":36,\"desiredDehumidity\":54,\"desiredFanMode\":\"on\",\"actualVOC\":-5002,\"actualCO2\":-5002,\"actualAQAccuracy\":0,\"actualAQScore\":-5002,\"desiredHeatRange\":[450,790],\"desiredCoolRange\":[650,920]}}],\"status\":{\"code\":0,\"message\":\"\"}}")
        assert self.ecobee.get_humidity() == 39
