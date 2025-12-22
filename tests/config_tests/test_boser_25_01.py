import unittest

from pyasic.config import FanModeConfig, TemperatureConfig


class TestBoserConfig25_01(unittest.TestCase):
    def test_fan_mode_handles_null_temperature(self):
        grpc_conf = {"temperature": None}
        self.assertEqual(FanModeConfig.default(), FanModeConfig.from_boser(grpc_conf))

    def test_fan_mode_handles_empty_manual(self):
        grpc_conf = {"temperature": {"manual": None, "minimumRequiredFans": None}}
        self.assertEqual(FanModeConfig.manual(), FanModeConfig.from_boser(grpc_conf))

    def test_fan_mode_auto_with_missing_min_fans(self):
        grpc_conf = {"temperature": {"auto": {}, "minimumRequiredFans": None}}
        self.assertEqual(FanModeConfig.normal(), FanModeConfig.from_boser(grpc_conf))

    def test_fan_mode_disabled_without_speed_defaults_to_immersion(self):
        grpc_conf = {"temperature": {"disabled": {}, "minimumRequiredFans": 0}}
        self.assertEqual(FanModeConfig.immersion(), FanModeConfig.from_boser(grpc_conf))

    def test_temperature_allows_partial_payload(self):
        grpc_conf = {"temperature": {"auto": {"targetTemperature": {"degreeC": 70}}}}
        self.assertEqual(
            TemperatureConfig(target=70), TemperatureConfig.from_boser(grpc_conf)
        )

    def test_temperature_returns_default_on_null(self):
        grpc_conf = {"temperature": None}
        self.assertEqual(
            TemperatureConfig.default(), TemperatureConfig.from_boser(grpc_conf)
        )


if __name__ == "__main__":
    unittest.main()
