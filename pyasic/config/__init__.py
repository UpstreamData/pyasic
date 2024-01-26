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
from dataclasses import asdict, dataclass, field

from pyasic.config.fans import FanModeConfig
from pyasic.config.mining import MiningModeConfig
from pyasic.config.pools import PoolConfig
from pyasic.config.power_scaling import PowerScalingConfig
from pyasic.config.temperature import TemperatureConfig
from pyasic.misc import merge_dicts


@dataclass
class MinerConfig:
    pools: PoolConfig = field(default_factory=PoolConfig.default)
    fan_mode: FanModeConfig = field(default_factory=FanModeConfig.default)
    temperature: TemperatureConfig = field(default_factory=TemperatureConfig.default)
    mining_mode: MiningModeConfig = field(default_factory=MiningModeConfig.default)
    power_scaling: PowerScalingConfig = field(
        default_factory=PowerScalingConfig.default
    )

    def as_dict(self) -> dict:
        return asdict(self)

    def as_am_modern(self, user_suffix: str = None) -> dict:
        return {
            **self.fan_mode.as_am_modern(),
            "freq-level": "100",
            **self.mining_mode.as_am_modern(),
            **self.pools.as_am_modern(user_suffix=user_suffix),
            **self.temperature.as_am_modern(),
            **self.power_scaling.as_am_modern(),
        }

    def as_wm(self, user_suffix: str = None) -> dict:
        return {
            **self.fan_mode.as_wm(),
            **self.mining_mode.as_wm(),
            **self.pools.as_wm(user_suffix=user_suffix),
            **self.temperature.as_wm(),
            **self.power_scaling.as_wm(),
        }

    def as_am_old(self, user_suffix: str = None) -> dict:
        return {
            **self.fan_mode.as_am_old(),
            **self.mining_mode.as_am_old(),
            **self.pools.as_am_old(user_suffix=user_suffix),
            **self.temperature.as_am_old(),
            **self.power_scaling.as_am_old(),
        }

    def as_goldshell(self, user_suffix: str = None) -> dict:
        return {
            **self.fan_mode.as_goldshell(),
            **self.mining_mode.as_goldshell(),
            **self.pools.as_goldshell(user_suffix=user_suffix),
            **self.temperature.as_goldshell(),
            **self.power_scaling.as_goldshell(),
        }

    def as_avalon(self, user_suffix: str = None) -> dict:
        return {
            **self.fan_mode.as_avalon(),
            **self.mining_mode.as_avalon(),
            **self.pools.as_avalon(user_suffix=user_suffix),
            **self.temperature.as_avalon(),
            **self.power_scaling.as_avalon(),
        }

    def as_inno(self, user_suffix: str = None) -> dict:
        return {
            **self.fan_mode.as_inno(),
            **self.mining_mode.as_inno(),
            **self.pools.as_inno(user_suffix=user_suffix),
            **self.temperature.as_inno(),
            **self.power_scaling.as_inno(),
        }

    def as_bosminer(self, user_suffix: str = None) -> dict:
        return {
            **merge_dicts(self.fan_mode.as_bosminer(), self.temperature.as_bosminer()),
            **self.mining_mode.as_bosminer(),
            **self.pools.as_bosminer(user_suffix=user_suffix),
            **self.power_scaling.as_bosminer(),
        }

    def as_boser(self, user_suffix: str = None) -> dict:
        return {
            **self.fan_mode.as_boser(),
            **self.temperature.as_boser(),
            **self.mining_mode.as_boser(),
            **self.pools.as_boser(user_suffix=user_suffix),
            **self.power_scaling.as_boser(),
        }

    def as_epic(self, user_suffix: str = None) -> dict:
        return {
            **merge_dicts(self.fan_mode.as_epic(), self.temperature.as_epic()),
            **self.mining_mode.as_epic(),
            **self.pools.as_epic(user_suffix=user_suffix),
            **self.power_scaling.as_epic(),
        }

    def as_auradine(self, user_suffix: str = None) -> dict:
        return {
            **self.fan_mode.as_auradine(),
            **self.temperature.as_auradine(),
            **self.mining_mode.as_auradine(),
            **self.pools.as_auradine(user_suffix=user_suffix),
            **self.power_scaling.as_auradine(),
        }

    @classmethod
    def from_dict(cls, dict_conf: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_dict(dict_conf.get("pools")),
            mining_mode=MiningModeConfig.from_dict(dict_conf.get("mining_mode")),
            fan_mode=FanModeConfig.from_dict(dict_conf.get("fan_mode")),
            temperature=TemperatureConfig.from_dict(dict_conf.get("temperature")),
            power_scaling=PowerScalingConfig.from_dict(dict_conf.get("power_scaling")),
        )

    @classmethod
    def from_api(cls, api_pools: dict) -> "MinerConfig":
        return cls(pools=PoolConfig.from_api(api_pools))

    @classmethod
    def from_am_modern(cls, web_conf: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_am_modern(web_conf),
            mining_mode=MiningModeConfig.from_am_modern(web_conf),
            fan_mode=FanModeConfig.from_am_modern(web_conf),
        )

    @classmethod
    def from_am_old(cls, web_conf: dict) -> "MinerConfig":
        return cls.from_am_modern(web_conf)

    @classmethod
    def from_goldshell(cls, web_conf: dict) -> "MinerConfig":
        return cls(pools=PoolConfig.from_am_modern(web_conf))

    @classmethod
    def from_inno(cls, web_pools: list) -> "MinerConfig":
        return cls(pools=PoolConfig.from_inno(web_pools))

    @classmethod
    def from_bosminer(cls, toml_conf: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_bosminer(toml_conf),
            mining_mode=MiningModeConfig.from_bosminer(toml_conf),
            fan_mode=FanModeConfig.from_bosminer(toml_conf),
            temperature=TemperatureConfig.from_bosminer(toml_conf),
            power_scaling=PowerScalingConfig.from_bosminer(toml_conf),
        )

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_boser(grpc_miner_conf),
            mining_mode=MiningModeConfig.from_boser(grpc_miner_conf),
            fan_mode=FanModeConfig.from_boser(grpc_miner_conf),
            temperature=TemperatureConfig.from_boser(grpc_miner_conf),
            power_scaling=PowerScalingConfig.from_boser(grpc_miner_conf),
        )

    @classmethod
    def from_epic(cls, web_conf: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_epic(web_conf),
            fan_mode=FanModeConfig.from_epic(web_conf),
            temperature=TemperatureConfig.from_epic(web_conf),
            mining_mode=MiningModeConfig.from_epic(web_conf),
        )

    @classmethod
    def from_vnish(cls, web_settings: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_vnish(web_settings),
            fan_mode=FanModeConfig.from_vnish(web_settings),
            temperature=TemperatureConfig.from_vnish(web_settings),
            mining_mode=MiningModeConfig.from_vnish(web_settings),
        )

    @classmethod
    def from_auradine(cls, web_conf: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_api(web_conf["pools"]),
            fan_mode=FanModeConfig.from_auradine(web_conf["fan"]),
            mining_mode=MiningModeConfig.from_auradine(web_conf["mode"]),
        )
