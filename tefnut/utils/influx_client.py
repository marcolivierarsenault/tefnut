import logging
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from tefnut.utils.setting import settings

client = None
write_api = None
logger = logging.getLogger("main")


class InfluxClient:
    def __init__(self):
        self.influx_enable = settings.get("influx.enable")
        if self.influx_enable:
            logger.info("Configuring Influx DB client")
            try:
                self.client = InfluxDBClient(url=settings.get("influx.url"),
                                             token=settings.get("influx.token"),
                                             org=settings.get("influx.org")
                                             )
                self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
                self.bucket = settings.get("influx.bucket")
            except Exception as e:
                logger.error("Faillure to configure Influx DB client")
                logger.error(e)
        else:
            logger.info("NOT Configuring Influx DB client")

    def write(self, point):
        if self.client is not None and self.write_api is not None:
            try:
                logger.debug("Wrinting to InfludDB")
                self.write_api.write(bucket=settings.get("influx.bucket"), org=settings.get("influx.org"), record=point)
            except Exception as e:
                logger.error("Faillure to configure Influx DB client")
                logger.error(e)
        else:
            logger.debug("Not Wrinting to InfludDB")
