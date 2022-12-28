import logging
import shelve
from datetime import datetime
from threading import Lock

import pyecobee as pyecobee
import pytz

from tefnut.utils.setting import settings

logger = logging.getLogger("main")

mutex = Lock()


class ecobee:
    def __init__(self, pyecobee_db_path):
        self.pyecobee_db_path = pyecobee_db_path
        try:
            mutex.acquire()
            pyecobee_db = shelve.open(pyecobee_db_path, protocol=2)
            self.ecobee_service = pyecobee_db["thermostat"]
        except KeyError:
            self.ecobee_service = pyecobee.EcobeeService(thermostat_name="thermostat",
                                                         application_key=settings.get("ECOBEE.apikey"))
        finally:
            pyecobee_db.close()
            mutex.release()

        if self.ecobee_service.authorization_token is None:
            self.authorize()

        if self.ecobee_service.access_token is None and self.ecobee_service.authorization_token is not None:
            self.request_tokens()

    def is_active(self):
        return (self.ecobee_service.authorization_token is not None and
                self.ecobee_service.access_token is not None and
                datetime.now(pytz.utc) <= self.ecobee_service.access_token_expires_on
                )

    def get_pin(self):
        mutex.acquire()
        self.pyecobee_db = shelve.open(self.pyecobee_db_path, protocol=2)
        if "pin" not in self.pyecobee_db.keys():
            pin = "0000-0000"
        else:
            pin = self.pyecobee_db["pin"]
        self.pyecobee_db.close()
        mutex.release()
        return pin

    def persist_to_shelf(self):
        mutex.acquire()
        self.pyecobee_db = shelve.open(self.pyecobee_db_path, protocol=2)
        self.pyecobee_db["thermostat"] = self.ecobee_service
        self.pyecobee_db.close()
        mutex.release()

    def persist_pin(self, pin):
        mutex.acquire()
        self.pyecobee_db = shelve.open(self.pyecobee_db_path, protocol=2)
        self.pyecobee_db["pin"] = pin
        self.pyecobee_db.close()
        mutex.release()

    def refresh_tokens(self):
        self.token_response = self.ecobee_service.refresh_tokens()
        logger.debug('TokenResponse returned from ecobee_service.refresh_tokens():\n{0}'.format(
            self.token_response.pretty_format()))
        self.persist_to_shelf()

    def request_tokens(self):
        try:
            self.token_response = self.ecobee_service.request_tokens()
            logger.debug('TokenResponse returned from ecobee_service.request_tokens():\n{0}'.format(
                self.token_response.pretty_format()))
            self.persist_to_shelf()
        except Exception:
            logger.warning("Please go congigure your PIN if not done: %s", self.get_pin())
            return -1

    def authorize(self):
        try:
            self.authorize_response = self.ecobee_service.authorize()
            logger.debug('AuthorizeResponse returned from ecobee_service.authorize():\n{0}'.format(
                self.authorize_response.pretty_format()))
            self.persist_to_shelf()
            logger.warning("Please go congigure your PIN if not done: %s", self.authorize_response.ecobee_pin)
            self.persist_pin(self.authorize_response.ecobee_pin)
        except Exception as e:
            logger.error("Failed to auhtorize ECOBEE apikey", exc_info=e)
            return -1

    def update_token(self):
        now_utc = datetime.now(pytz.utc)
        if now_utc > self.ecobee_service.refresh_token_expires_on:
            self.authorize()
            self.request_tokens()
        elif now_utc > self.ecobee_service.access_token_expires_on:
            self.token_response = self.refresh_tokens()

    def get_humidity(self):
        try:
            self.update_token()
            selection = pyecobee.Selection(selection_type=pyecobee.SelectionType.REGISTERED.value, selection_match='',
                                           include_runtime=True)
            thermostat_response = self.ecobee_service.request_thermostats(selection)
            logger.debug(thermostat_response)
            return thermostat_response.thermostat_list[0].runtime.actual_humidity
        except Exception as e:
            logger.warning("Failed to retreive humidity", exc_info=e)
