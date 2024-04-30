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

    def test_epic_deserialize_and_serialize(self):
        for fan_mode in FanModeConfig:
            with self.subTest(
                msg=f"Test serialization and deserialization of epic fan config",
                fan_mode=fan_mode,
            ):
                conf = fan_mode()
                epic_conf = conf.as_epic()
                self.assertEqual(conf, FanModeConfig.from_epic(epic_conf))

    def test_vnish_deserialize_and_serialize(self):
        for fan_mode in FanModeConfig:
            with self.subTest(
                msg=f"Test serialization and deserialization of vnish fan config",
                fan_mode=fan_mode,
            ):
                conf = fan_mode()
                vnish_conf = conf.as_vnish()
                self.assertEqual(conf, FanModeConfig.from_vnish(vnish_conf))

    def test_auradine_deserialize_and_serialize(self):
        for fan_mode in FanModeConfig:
            with self.subTest(
                msg=f"Test serialization and deserialization of auradine fan config",
                fan_mode=fan_mode,
            ):
                conf = fan_mode()
                aur_conf = conf.as_auradine()
                self.assertEqual(conf, FanModeConfig.from_auradine(aur_conf))

    def test_boser_deserialize_and_serialize(self):
        for fan_mode in FanModeConfig:
            with self.subTest(
                msg=f"Test serialization and deserialization of boser fan config",
                fan_mode=fan_mode,
            ):
                conf = fan_mode()
                boser_conf = conf.as_boser()
                self.assertEqual(conf, FanModeConfig.from_boser(boser_conf))
