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

from pydantic import BaseModel, Field

from pyasic.config.fans import FanMode, FanModeConfig, FanModeNormal
from pyasic.config.mining import MiningMode, MiningModeConfig
from pyasic.config.mining.scaling import ScalingConfig
from pyasic.config.pools import PoolConfig
from pyasic.config.temperature import TemperatureConfig
from pyasic.misc import merge_dicts


class MinerConfig(BaseModel):
    """Represents the configuration for a miner including pool configuration,
    fan mode, temperature settings, mining mode, and power scaling."""

    class Config:
        arbitrary_types_allowed = True

    pools: PoolConfig = Field(default_factory=PoolConfig.default)
    fan_mode: FanMode = Field(default_factory=FanModeConfig.default)
    temperature: TemperatureConfig = Field(default_factory=TemperatureConfig.default)
    mining_mode: MiningMode = Field(default_factory=MiningModeConfig.default)

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError

    def as_dict(self) -> dict:
        """Converts the MinerConfig object to a dictionary."""
        return self.model_dump()

    def as_am_modern(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for modern Antminers."""
        return {
            **self.fan_mode.as_am_modern(),
            "freq-level": "100",
            **self.mining_mode.as_am_modern(),
            **self.pools.as_am_modern(user_suffix=user_suffix),
            **self.temperature.as_am_modern(),
        }

    def as_hiveon_modern(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for modern Hiveon."""
        return {
            **self.fan_mode.as_hiveon_modern(),
            "freq-level": "100",
            **self.mining_mode.as_hiveon_modern(),
            **self.pools.as_hiveon_modern(user_suffix=user_suffix),
            **self.temperature.as_hiveon_modern(),
        }

    def as_elphapex(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for modern Elphapex."""
        return {
            **self.fan_mode.as_elphapex(),
            "fc-freq-level": "100",
            **self.mining_mode.as_elphapex(),
            **self.pools.as_elphapex(user_suffix=user_suffix),
            **self.temperature.as_elphapex(),
        }

    def as_wm(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for Whatsminers."""
        return {
            **self.fan_mode.as_wm(),
            **self.mining_mode.as_wm(),
            **self.pools.as_wm(user_suffix=user_suffix),
            **self.temperature.as_wm(),
        }

    def as_am_old(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for old versions of Antminers."""
        return {
            **self.fan_mode.as_am_old(),
            **self.mining_mode.as_am_old(),
            **self.pools.as_am_old(user_suffix=user_suffix),
            **self.temperature.as_am_old(),
        }

    def as_goldshell(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for Goldshell miners."""
        return {
            **self.fan_mode.as_goldshell(),
            **self.mining_mode.as_goldshell(),
            **self.pools.as_goldshell(user_suffix=user_suffix),
            **self.temperature.as_goldshell(),
        }

    def as_avalon(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for Avalonminers."""
        return {
            **self.fan_mode.as_avalon(),
            **self.mining_mode.as_avalon(),
            **self.pools.as_avalon(user_suffix=user_suffix),
            **self.temperature.as_avalon(),
        }

    def as_inno(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for Innosilicon miners."""
        return {
            **self.fan_mode.as_inno(),
            **self.mining_mode.as_inno(),
            **self.pools.as_inno(user_suffix=user_suffix),
            **self.temperature.as_inno(),
        }

    def as_bosminer(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the bosminer.toml format."""
        return {
            **merge_dicts(self.fan_mode.as_bosminer(), self.temperature.as_bosminer()),
            **self.mining_mode.as_bosminer(),
            **self.pools.as_bosminer(user_suffix=user_suffix),
        }

    def as_boser(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for BOSer."""
        return {
            **self.fan_mode.as_boser(),
            **self.temperature.as_boser(),
            **self.mining_mode.as_boser(),
            **self.pools.as_boser(user_suffix=user_suffix),
        }

    def as_epic(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for ePIC miners."""
        return {
            **merge_dicts(self.fan_mode.as_epic(), self.temperature.as_epic()),
            **self.mining_mode.as_epic(),
            **self.pools.as_epic(user_suffix=user_suffix),
        }

    def as_auradine(self, user_suffix: str | None = None) -> dict:
        """Generates the configuration in the format suitable for Auradine miners."""
        return {
            **self.fan_mode.as_auradine(),
            **self.temperature.as_auradine(),
            **self.mining_mode.as_auradine(),
            **self.pools.as_auradine(user_suffix=user_suffix),
        }

    def as_mara(self, user_suffix: str | None = None) -> dict:
        return {
            **self.fan_mode.as_mara(),
            **self.temperature.as_mara(),
            **self.mining_mode.as_mara(),
            **self.pools.as_mara(user_suffix=user_suffix),
        }

    def as_espminer(self, user_suffix: str | None = None) -> dict:
        return {
            **self.fan_mode.as_espminer(),
            **self.temperature.as_espminer(),
            **self.mining_mode.as_espminer(),
            **self.pools.as_espminer(user_suffix=user_suffix),
        }

    def as_luxos(self, user_suffix: str | None = None) -> dict:
        return {
            **self.fan_mode.as_luxos(),
            **self.temperature.as_luxos(),
            **self.mining_mode.as_luxos(),
            **self.pools.as_luxos(user_suffix=user_suffix),
        }

    def as_vnish(self, user_suffix: str | None = None) -> dict:
        main_cfg = {
            "miner": {
                **self.fan_mode.as_vnish(),
                **self.temperature.as_vnish(),
                **self.mining_mode.as_vnish(),
                **self.pools.as_vnish(user_suffix=user_suffix),
            }
        }
        if isinstance(self.fan_mode, FanModeNormal):
            main_cfg["miner"]["cooling"]["mode"]["param"] = self.temperature.target
        return main_cfg

    def as_hammer(self, *args, **kwargs) -> dict:
        return self.as_am_modern(*args, **kwargs)

    @classmethod
    def from_dict(cls, dict_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from a dictionary."""
        return cls(
            pools=PoolConfig.from_dict(dict_conf.get("pools")),
            mining_mode=MiningModeConfig.from_dict(dict_conf.get("mining_mode")),
            fan_mode=FanModeConfig.from_dict(dict_conf.get("fan_mode")),
            temperature=TemperatureConfig.from_dict(dict_conf.get("temperature")),
        )

    @classmethod
    def from_api(cls, api_pools: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from API pool data."""
        return cls(pools=PoolConfig.from_api(api_pools))

    @classmethod
    def from_am_modern(cls, web_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from web configuration for modern Antminers."""
        return cls(
            pools=PoolConfig.from_am_modern(web_conf),
            mining_mode=MiningModeConfig.from_am_modern(web_conf),
            fan_mode=FanModeConfig.from_am_modern(web_conf),
        )

    @classmethod
    def from_hiveon_modern(cls, web_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from web configuration for Hiveon."""
        return cls(
            pools=PoolConfig.from_hiveon_modern(web_conf),
            mining_mode=MiningModeConfig.from_hiveon_modern(web_conf),
            fan_mode=FanModeConfig.from_hiveon_modern(web_conf),
        )

    @classmethod
    def from_elphapex(cls, web_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from web configuration for modern Antminers."""
        return cls(
            pools=PoolConfig.from_elphapex(web_conf),
            mining_mode=MiningModeConfig.from_elphapex(web_conf),
            fan_mode=FanModeConfig.from_elphapex(web_conf),
        )

    @classmethod
    def from_am_old(cls, web_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from web configuration for old versions of Antminers."""
        return cls.from_am_modern(web_conf)

    @classmethod
    def from_goldshell(cls, web_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from web configuration for Goldshell miners."""
        return cls(pools=PoolConfig.from_am_modern(web_conf))

    @classmethod
    def from_inno(cls, web_pools: list) -> "MinerConfig":
        """Constructs a MinerConfig object from web configuration for Innosilicon miners."""
        return cls(pools=PoolConfig.from_inno(web_pools))

    @classmethod
    def from_bosminer(cls, toml_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from the bosminer.toml file, same as the `as_bosminer` dumps a dict for writing to that file as toml."""
        return cls(
            pools=PoolConfig.from_bosminer(toml_conf),
            mining_mode=MiningModeConfig.from_bosminer(toml_conf),
            fan_mode=FanModeConfig.from_bosminer(toml_conf),
            temperature=TemperatureConfig.from_bosminer(toml_conf),
        )

    @classmethod
    def from_boser(cls, grpc_miner_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from gRPC configuration for BOSer."""
        return cls(
            pools=PoolConfig.from_boser(grpc_miner_conf),
            mining_mode=MiningModeConfig.from_boser(grpc_miner_conf),
            fan_mode=FanModeConfig.from_boser(grpc_miner_conf),
            temperature=TemperatureConfig.from_boser(grpc_miner_conf),
        )

    @classmethod
    def from_epic(cls, web_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from web configuration for ePIC miners."""
        return cls(
            pools=PoolConfig.from_epic(web_conf),
            fan_mode=FanModeConfig.from_epic(web_conf),
            temperature=TemperatureConfig.from_epic(web_conf),
            mining_mode=MiningModeConfig.from_epic(web_conf),
        )

    @classmethod
    def from_vnish(cls, web_settings: dict, web_presets: list[dict]) -> "MinerConfig":
        """Constructs a MinerConfig object from web settings for VNish miners."""
        return cls(
            pools=PoolConfig.from_vnish(web_settings),
            fan_mode=FanModeConfig.from_vnish(web_settings),
            temperature=TemperatureConfig.from_vnish(web_settings),
            mining_mode=MiningModeConfig.from_vnish(web_settings, web_presets),
        )

    @classmethod
    def from_auradine(cls, web_conf: dict) -> "MinerConfig":
        """Constructs a MinerConfig object from web configuration for Auradine miners."""
        return cls(
            pools=PoolConfig.from_api(web_conf["pools"]),
            fan_mode=FanModeConfig.from_auradine(web_conf["fan"]),
            mining_mode=MiningModeConfig.from_auradine(web_conf["mode"]),
        )

    @classmethod
    def from_mara(cls, web_miner_config: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_mara(web_miner_config),
            fan_mode=FanModeConfig.from_mara(web_miner_config),
            mining_mode=MiningModeConfig.from_mara(web_miner_config),
        )

    @classmethod
    def from_espminer(cls, web_system_info: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_espminer(web_system_info),
            fan_mode=FanModeConfig.from_espminer(web_system_info),
        )

    @classmethod
    def from_iceriver(cls, web_userpanel: dict) -> "MinerConfig":
        return cls(
            pools=PoolConfig.from_iceriver(web_userpanel),
        )

    @classmethod
    def from_luxos(
        cls,
        rpc_tempctrl: dict,
        rpc_fans: dict,
        rpc_pools: dict,
        rpc_groups: dict,
        rpc_config: dict,
        rpc_profiles: dict,
    ) -> "MinerConfig":
        return cls(
            temperature=TemperatureConfig.from_luxos(rpc_tempctrl=rpc_tempctrl),
            fan_mode=FanModeConfig.from_luxos(
                rpc_tempctrl=rpc_tempctrl, rpc_fans=rpc_fans
            ),
            pools=PoolConfig.from_luxos(rpc_pools=rpc_pools, rpc_groups=rpc_groups),
            mining_mode=MiningModeConfig.from_luxos(
                rpc_config=rpc_config, rpc_profiles=rpc_profiles
            ),
        )

    @classmethod
    def from_hammer(cls, *args, **kwargs) -> "MinerConfig":
        return cls.from_am_modern(*args, **kwargs)
