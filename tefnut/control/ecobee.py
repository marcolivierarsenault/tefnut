import shelve
import logging
import pytz
import pyecobee as pyecobee
from datetime import datetime
from tefnut.utils.setting import settings

logger = logging.getLogger("main")


def get_pin():
    pyecobee_db = shelve.open("pyecobee_db", protocol=2)
    pin = pyecobee_db["pin"]
    pyecobee_db.close()
    return pin


class ecobee:
    def __init__(self):
        try:
            pyecobee_db = shelve.open('pyecobee_db', protocol=2)
            self.ecobee_service = pyecobee_db["thermostat"]
        except KeyError:
            self.ecobee_service = pyecobee.EcobeeService(thermostat_name="thermostat",
                                                         application_key=settings.get("ECOBEE.apikey"))
        finally:
            pyecobee_db.close()

        if self.ecobee_service.authorization_token is None:
            self.authorize()

        if self.ecobee_service.access_token is None:
            self.request_tokens()

    def persist_to_shelf(self):
        self.pyecobee_db = shelve.open("pyecobee_db", protocol=2)
        self.pyecobee_db["thermostat"] = self.ecobee_service
        self.pyecobee_db.close()

    def persist_pin(self, pin):
        self.pyecobee_db = shelve.open("pyecobee_db", protocol=2)
        self.pyecobee_db["pin"] = pin
        self.pyecobee_db.close()

    def refresh_tokens(self):
        self.token_response = self.ecobee_service.refresh_tokens()
        logger.debug('TokenResponse returned from ecobee_service.refresh_tokens():\n{0}'.format(
            self.token_response.pretty_format()))
        self.persist_to_shelf()

    def request_tokens(self):
        self.token_response = self.ecobee_service.request_tokens()
        logger.debug('TokenResponse returned from ecobee_service.request_tokens():\n{0}'.format(
            self.token_response.pretty_format()))
        self.persist_to_shelf()

    def authorize(self):
        self.authorize_response = self.ecobee_service.authorize()
        logger.debug('AutorizeResponse returned from ecobee_service.authorize():\n{0}'.format(
            self.authorize_response.pretty_format()))
        self.persist_to_shelf()
        logger.warning("Please go congigure your PIN if not done: %s", self.authorize_response.ecobee_pin)
        self.persist_pin(self.authorize_response.ecobee_pin)

    def get_humidity(self):

        try:
            now_utc = datetime.now(pytz.utc)
            if now_utc > self.ecobee_service.refresh_token_expires_on:
                self.authorize()
                self.request_tokens()
            elif now_utc > self.ecobee_service.access_token_expires_on:
                self.token_response = self.refresh_tokens()

            selection = pyecobee.Selection(selection_type=pyecobee.SelectionType.REGISTERED.value, selection_match='',
                                           include_runtime=True)
            thermostat_response = self.ecobee_service.request_thermostats(selection)
            logger.debug(thermostat_response)
            return thermostat_response.thermostat_list[0].runtime.actual_humidity
        except Exception as e:
            logger.error("Failed to retreive humidity", exc_info=e)
