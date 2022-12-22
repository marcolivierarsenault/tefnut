from tefnut.utils.setting import settings


class Humidifier:
    def __init__(self):
        if settings.get("GENERAL.humidifier") == "pi":  # pragma: no cover
            from tefnut.control.humi_pi import HumidifierImplement
            self.humi = HumidifierImplement()
        else:
            from tefnut.control.humi_stub import HumidifierImplement
            self.humi = HumidifierImplement()

    def turn_on(self):
        self.humi.turn_on()

    def turn_off(self):
        self.humi.turn_off()

    def get_value(self):
        return self.humi.get_value()

    def shutdown(self):
        self.humi.shutdown()
