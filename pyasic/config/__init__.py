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
from dataclasses import dataclass

from pyasic.config.fans import FanModeConfig
from pyasic.config.mining import MiningModeConfig
from pyasic.config.pools import PoolConfig
from pyasic.config.power_scaling import PowerScalingConfig
from pyasic.config.temperature import TemperatureConfig


@dataclass
class MinerConfig:
    pools: PoolConfig = PoolConfig.default()
    mining_mode: MiningModeConfig = MiningModeConfig.default()
    fan_mode: FanModeConfig = FanModeConfig.default()
    temperature: TemperatureConfig = TemperatureConfig.default()
    power_scaling: PowerScalingConfig = PowerScalingConfig.default()

    def as_am_modern(self, user_suffix: str = None):
        return {
            **self.fan_mode.as_am_modern(),
            "freq-level": "100",
            **self.mining_mode.as_am_modern(),
            **self.pools.as_am_modern(user_suffix=user_suffix),
            **self.temperature.as_am_modern(),
            **self.power_scaling.as_am_modern(),
        }

    def as_wm(self, user_suffix: str = None):
        return {
            **self.fan_mode.as_wm(),
            **self.mining_mode.as_wm(),
            **self.pools.as_wm(user_suffix=user_suffix),
            **self.temperature.as_wm(),
            **self.power_scaling.as_wm(),
        }

    def as_am_old(self, user_suffix: str = None):
        return {
            **self.fan_mode.as_am_old(),
            **self.mining_mode.as_am_old(),
            **self.pools.as_am_old(user_suffix=user_suffix),
            **self.temperature.as_am_old(),
            **self.power_scaling.as_am_old(),
        }


if __name__ == "__main__":
    config = MinerConfig(
        pools=PoolConfig.simple(
            [
                {
                    "url": "stratum+tcp://stratum.test.io:3333",
                    "user": "user.test",
                    "password": "123",
                }
            ]
        ),
        mining_mode=MiningModeConfig.power_tuning(3000),
    )
    print(config.as_wm())
    print(config.as_am_modern())
    print(config.as_am_old())
