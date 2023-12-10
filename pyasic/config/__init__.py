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

import toml

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

    def as_goldshell(self, user_suffix: str = None):
        return {
            **self.fan_mode.as_goldshell(),
            **self.mining_mode.as_goldshell(),
            **self.pools.as_goldshell(user_suffix=user_suffix),
            **self.temperature.as_goldshell(),
            **self.power_scaling.as_goldshell(),
        }

    def as_avalon(self, user_suffix: str = None):
        return {
            **self.fan_mode.as_avalon(),
            **self.mining_mode.as_avalon(),
            **self.pools.as_avalon(user_suffix=user_suffix),
            **self.temperature.as_avalon(),
            **self.power_scaling.as_avalon(),
        }

    def as_inno(self, user_suffix: str = None):
        return {
            **self.fan_mode.as_inno(),
            **self.mining_mode.as_inno(),
            **self.pools.as_inno(user_suffix=user_suffix),
            **self.temperature.as_inno(),
            **self.power_scaling.as_inno(),
        }

    def as_bosminer(self, user_suffix: str = None):
        return {
            **merge(self.fan_mode.as_bosminer(), self.temperature.as_bosminer()),
            **self.mining_mode.as_bosminer(),
            **self.pools.as_bosminer(user_suffix=user_suffix),
            **self.power_scaling.as_bosminer(),
        }

    @classmethod
    def from_api(cls, api_pools: dict):
        return cls(pools=PoolConfig.from_api(api_pools))

    @classmethod
    def from_am_modern(cls, web_conf: dict):
        return cls(
            pools=PoolConfig.from_am_modern(web_conf),
            mining_mode=MiningModeConfig.from_am_modern(web_conf),
            fan_mode=FanModeConfig.from_am_modern(web_conf),
        )

    @classmethod
    def from_am_old(cls, web_conf: dict):
        return cls.from_am_modern(web_conf)

    @classmethod
    def from_goldshell(cls, web_conf: dict):
        return cls(pools=PoolConfig.from_am_modern(web_conf))

    @classmethod
    def from_inno(cls, web_pools: dict):
        return cls(pools=PoolConfig.from_inno(web_pools))


def merge(a: dict, b: dict):
    ret = {}
    for k in a:
        v = a[k]
        if k in b.keys():
            if isinstance(v, dict):
                ret[k] = merge(a[k], b[k])
            elif isinstance(v, list):
                ret[k] = [*v, *b[k]]
            else:
                ret[k] = v
        else:
            ret[k] = v
    for k in b:
        v = b[k]
        if k not in ret.keys():
            ret[k] = v
    return ret


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
        temperature=TemperatureConfig(hot=100),
        fan_mode=FanModeConfig.manual(minimum_fans=2, speed=70),
    )
    print("WM:", config.as_wm())
    print("AM Modern:", config.as_am_modern())
    print("AM Old:", config.as_am_old())
    print("GS:", config.as_goldshell())
    print("Avalon:", config.as_avalon())
    print("Inno:", config.as_inno())
    print("BOS+ .toml:", config.as_bosminer())
    print("BOS+ .toml as toml:")
    print(toml.dumps(config.as_bosminer()))
