import unittest

from pyasic.config import FanModeConfig


class TestFanConfig(unittest.TestCase):
    def test_serialize_and_deserialize(self):
        for fan_mode in FanModeConfig:
            with self.subTest(
                msg=f"Test serialization and deserialization of fan config",
                fan_mode=fan_mode,
            ):
                conf = fan_mode()
                dict_conf = conf.as_dict()
                self.assertEqual(conf, FanModeConfig.from_dict(dict_conf))

    def test_bosminer_deserialize_and_serialize(self):
        for fan_mode in FanModeConfig:
            with self.subTest(
                msg=f"Test serialization and deserialization of bosminer fan config",
                fan_mode=fan_mode,
            ):
                conf = fan_mode()
                bos_conf = conf.as_bosminer()
                self.assertEqual(conf, FanModeConfig.from_bosminer(bos_conf))

    def test_am_modern_deserialize_and_serialize(self):
        for fan_mode in FanModeConfig:
            with self.subTest(
                msg=f"Test serialization and deserialization of antminer modern fan config",
                fan_mode=fan_mode,
            ):
                conf = fan_mode()
                am_conf = conf.as_am_modern()
                self.assertEqual(conf, FanModeConfig.from_am_modern(am_conf))
