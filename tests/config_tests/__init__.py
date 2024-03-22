# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------
import unittest

from pyasic.config import (
    FanModeConfig,
    MinerConfig,
    MiningModeConfig,
    PoolConfig,
    PowerScalingConfig,
    TemperatureConfig,
)
from pyasic.config.power_scaling import PowerScalingShutdown


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.cfg = MinerConfig(
            pools=PoolConfig.simple(
                [
                    {
                        "url": "stratum+tcp://stratum.test.io:3333",
                        "user": "test.test",
                        "password": "123",
                    }
                ]
            ),
            fan_mode=FanModeConfig.manual(speed=90, minimum_fans=2),
            temperature=TemperatureConfig(target=70, danger=120),
            mining_mode=MiningModeConfig.power_tuning(power=3000),
            power_scaling=PowerScalingConfig.enabled(
                power_step=100,
                minimum_power=2000,
                shutdown_enabled=PowerScalingShutdown.enabled(duration=3),
            ),
        )

    def test_dict_deserialize_and_serialize(self):
        dict_config = self.cfg.as_dict()
        loaded_cfg = MinerConfig.from_dict(dict_config)
        self.assertEqual(loaded_cfg, self.cfg)

    def test_dict_serialize_and_deserialize(self):
        dict_config = {
            "pools": {
                "groups": [
                    {
                        "pools": [
                            {
                                "url": "stratum+tcp://stratum.test.io:3333",
                                "user": "test.test",
                                "password": "123",
                            }
                        ],
                        "quota": 1,
                        "name": "B6SPD2",
                    }
                ]
            },
            "fan_mode": {"mode": "manual", "speed": 90, "minimum_fans": 2},
            "temperature": {"target": 70, "hot": None, "danger": 120},
            "mining_mode": {"mode": "power_tuning", "power": 3000, "algo": {}},
            "power_scaling": {
                "mode": "enabled",
                "power_step": 100,
                "minimum_power": 2000,
                "shutdown_enabled": {"mode": "enabled", "duration": 3},
            },
        }

        loaded_config = MinerConfig.from_dict(dict_config)
        dumped_config = loaded_config.as_dict()
        self.assertEqual(dumped_config, dict_config)

    def test_bosminer_deserialize_and_serialize(self):
        bosminer_config = self.cfg.as_bosminer()
        loaded_config = MinerConfig.from_bosminer(bosminer_config)
        self.assertEqual(loaded_config, self.cfg)

    def test_bosminer_serialize_and_deserialize(self):
        bosminer_config = {
            "temp_control": {
                "mode": "manual",
                "target_temp": 70,
                "dangerous_temp": 120,
            },
            "fan_control": {"min_fans": 2, "speed": 90},
            "autotuning": {"enabled": True, "psu_power_limit": 3000},
            "group": [
                {
                    "name": "W91Q1L",
                    "pool": [
                        {
                            "url": "statum+tcp://stratum.test.io:3333",
                            "user": "test.test",
                            "password": "123",
                        }
                    ],
                    "quota": 1,
                }
            ],
            "power_scaling": {
                "enabled": True,
                "power_step": 100,
                "min_psu_power_limit": 2000,
                "shutdown_enabled": True,
                "shutdown_duration": 3,
            },
        }

        loaded_config = MinerConfig.from_bosminer(bosminer_config)
        dumped_config = loaded_config.as_bosminer()
        self.assertEqual(dumped_config, bosminer_config)

    def test_am_modern_serialize(self):
        correct_config = {
            "bitmain-fan-ctrl": True,
            "bitmain-fan-pwm": "90",
            "freq-level": "100",
            "miner-mode": 0,
            "pools": [
                {
                    "url": "stratum+tcp://stratum.test.io:3333",
                    "user": "test.test",
                    "pass": "123",
                },
                {"url": "", "user": "", "pass": ""},
                {"url": "", "user": "", "pass": ""},
            ],
        }

        self.assertEqual(correct_config, self.cfg.as_am_modern())

    def test_am_old_serialize(self):
        correct_config = {
            "_ant_pool1url": "stratum+tcp://stratum.test.io:3333",
            "_ant_pool1user": "test.test",
            "_ant_pool1pw": "123",
            "_ant_pool2url": "",
            "_ant_pool2user": "",
            "_ant_pool2pw": "",
            "_ant_pool3url": "",
            "_ant_pool3user": "",
            "_ant_pool3pw": "",
        }

        self.assertEqual(correct_config, self.cfg.as_am_old())

    def test_wm_serialize(self):
        correct_config = {
            "mode": "power_tuning",
            "power_tuning": {"wattage": 3000},
            "pools": {
                "pool_1": "stratum+tcp://stratum.test.io:3333",
                "worker_1": "test.test",
                "passwd_1": "123",
                "pool_2": "",
                "worker_2": "",
                "passwd_2": "",
                "pool_3": "",
                "worker_3": "",
                "passwd_3": "",
            },
        }

        self.assertEqual(correct_config, self.cfg.as_wm())

    def test_goldshell_serialize(self):
        correct_config = {
            "pools": [
                {
                    "url": "stratum+tcp://stratum.test.io:3333",
                    "user": "test.test",
                    "pass": "123",
                }
            ]
        }

        self.assertEqual(correct_config, self.cfg.as_goldshell())

    def test_avalon_serialize(self):
        correct_config = {"pools": "stratum+tcp://stratum.test.io:3333,test.test,123"}

        self.assertEqual(correct_config, self.cfg.as_avalon())

    def test_inno_serialize(self):
        correct_config = {
            "Pool1": "stratum+tcp://stratum.test.io:3333",
            "UserName1": "test.test",
            "Password1": "123",
            "Pool2": "",
            "UserName2": "",
            "Password2": "",
            "Pool3": "",
            "UserName3": "",
            "Password3": "",
        }

        self.assertEqual(correct_config, self.cfg.as_inno())


if __name__ == "__main__":
    unittest.main()
