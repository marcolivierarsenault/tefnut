from enum import Enum


class MODE(Enum):
    AUTO = 0
    MANUAL = 1
    TEMP_EMERGENCY = 2
    NO_HUMIDITY = 3


class STATE(Enum):
    OFF = 0
    ON = 1
