#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import unittest

from tests.test_data import (
    bosminer_api_pools,
    bosminer_config_pools,
    x19_api_pools,
    x19_web_pools,
)

from pyasic.config import MinerConfig, _Pool, _PoolGroup  # noqa


class ConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self.test_config = MinerConfig(
            pool_groups=[
                _PoolGroup(
                    quota=1,
                    group_name="TEST",
                    pools=[
                        _Pool(
                            url="stratum+tcp://pyasic.testpool_1.pool:3333",
                            username="pyasic.test",
                            password="123",
                        ),
                        _Pool(
                            url="stratum+tcp://pyasic.testpool_2.pool:3333",
                            username="pyasic.test",
                            password="123",
                        ),
                    ],
                )
            ],
            temp_mode="auto",
            temp_target=70.0,
            temp_hot=80.0,
            temp_dangerous=100.0,
            fan_speed=None,
            autotuning_enabled=True,
            autotuning_wattage=900,
        )

    def test_config_from_raw(self):
        bos_config = MinerConfig().from_raw(bosminer_config_pools)
        bos_config.pool_groups[0].group_name = "TEST"

        with self.subTest(
            msg="Testing BOSMiner config file config.", bos_config=bos_config
        ):
            self.assertEqual(bos_config, self.test_config)

        x19_cfg = MinerConfig().from_raw(x19_web_pools)
        x19_cfg.pool_groups[0].group_name = "TEST"

        with self.subTest(msg="Testing X19 API config.", x19_cfg=x19_cfg):
            self.assertEqual(x19_cfg, self.test_config)

    def test_config_from_api(self):
        bos_cfg = MinerConfig().from_api(bosminer_api_pools["POOLS"])
        bos_cfg.pool_groups[0].group_name = "TEST"

        with self.subTest(msg="Testing BOSMiner API config.", bos_cfg=bos_cfg):
            self.assertEqual(bos_cfg, self.test_config)

        x19_cfg = MinerConfig().from_api(x19_api_pools["POOLS"])
        x19_cfg.pool_groups[0].group_name = "TEST"

        with self.subTest(msg="Testing X19 API config.", x19_cfg=x19_cfg):
            self.assertEqual(x19_cfg, self.test_config)

    def test_config_as_types(self):
        cfg = MinerConfig().from_api(bosminer_api_pools["POOLS"])
        cfg.pool_groups[0].group_name = "TEST"

        commands = [
            func
            for func in
            # each function in self
            dir(cfg)
            if callable(getattr(cfg, func)) and
            # no __ methods
            not func.startswith("__")
        ]

        for command in [cmd for cmd in commands if cmd.startswith("as_")]:
            with self.subTest():
                output = getattr(cfg, command)()
                self.assertEqual(output, getattr(self.test_config, command)())
                if f"from_{command.split('as_')[1]}" in commands:
                    self.assertEqual(
                        getattr(MinerConfig(), f"from_{command.split('as_')[1]}")(
                            output
                        ),
                        self.test_config,
                    )


if __name__ == "__main__":
    unittest.main()
