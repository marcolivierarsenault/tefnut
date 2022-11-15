from tefnut.utils.setting import settings


class Humidificator:
    def __init__(self):
        if settings.get("GENERAL.humidificator") == "pi":
            from tefnut.control.humidificator_pi import HumidificatorImplement
            self.humi = HumidificatorImplement()
        else:
            from tefnut.control.humidificator_stub import HumidificatorImplement
            self.humi = HumidificatorImplement()

    def turn_on(self):
        self.humi.turn_on()

    def turn_off(self):
        self.humi.turn_off()

    def get_value(self):
        return self.humi.get_value()

    def shutdown(self):
        self.humi.shutdown()
