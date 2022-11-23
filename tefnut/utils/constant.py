from enum import Enum


class MODE(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"
    TEMP_EMERGENCY = "TEMP_EMERGENCY"
    NO_HUMIDITY = "NO_HUMIDITY"
    OFF = "OFF"


class STATE(str, Enum):
    OFF = "OFF"
    ON = "ON"
