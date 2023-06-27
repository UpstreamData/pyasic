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
import asyncio
import logging
from collections import namedtuple
from typing import List, Optional, Tuple, Union

import toml

from pyasic.API.bosminer import BOSMinerAPI
from pyasic.API.luxminer import LUXMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import BraiinsOSError, MinerErrorData
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.web.bosminer import BOSMinerWebAPI

LUXMINER_DATA_LOC = {
    "mac": {
        "cmd": "get_mac",
        "kwargs": {"api_config": {"api": "config"}},
    },
    "model": {"cmd": "get_model", "kwargs": {}},
    "api_ver": {
        "cmd": "get_api_ver",
        "kwargs": {},
    },
    "fw_ver": {
        "cmd": "get_fw_ver",
        "kwargs": {},
    },
    "hostname": {
        "cmd": "get_hostname",
        "kwargs": {},
    },
    "hashrate": {
        "cmd": "get_hashrate",
        "kwargs": {},
    },
    "nominal_hashrate": {
        "cmd": "get_nominal_hashrate",
        "kwargs": {},
    },
    "hashboards": {
        "cmd": "get_hashboards",
        "kwargs": {},
    },
    "wattage": {
        "cmd": "get_wattage",
        "kwargs": {},
    },
    "wattage_limit": {
        "cmd": "get_wattage_limit",
        "kwargs": {},
    },
    "fans": {
        "cmd": "get_fans",
        "kwargs": {},
    },
    "fan_psu": {"cmd": "get_fan_psu", "kwargs": {}},
    "env_temp": {"cmd": "get_env_temp", "kwargs": {}},
    "errors": {
        "cmd": "get_errors",
        "kwargs": {},
    },
    "fault_light": {
        "cmd": "get_fault_light",
        "kwargs": {},
    },
    "pools": {
        "cmd": "get_pools",
        "kwargs": {},
    },
    "is_mining": {
        "cmd": "is_mining",
        "kwargs": {},
    },
    "uptime": {
        "cmd": "get_uptime",
        "kwargs": {"api_stats": {"api": "stats"}},
    },
}


class LUXMiner(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        # interfaces
        self.api = LUXMinerAPI(ip, api_ver)
        # self.web = BOSMinerWebAPI(ip)

        # static data
        self.api_type = "LUXMiner"
        # data gathering locations
        self.data_locations = LUXMINER_DATA_LOC
        # autotuning/shutdown support
        # self.supports_autotuning = True
        # self.supports_shutdown = True

        # data storage
        self.api_ver = api_ver

    async def _get_session(self) -> Optional[str]:
        try:
            data = await self.api.session()
            if not data["SESSION"][0]["SessionID"] == "":
                return data["SESSION"][0]["SessionID"]
        except APIError:
            pass

        try:
            data = await self.api.logon()
            return data["SESSION"][0]["SessionID"]
        except (LookupError, APIError):
            return

    async def fault_light_on(self) -> bool:
        """Sends command to turn on fault light on the miner."""
        try:
            session_id = await self._get_session()
            if session_id:
                await self.api.ledset(session_id, "red", "blink")
            return True
        except (APIError, LookupError):
            pass
        return False

    async def fault_light_off(self) -> bool:
        """Sends command to turn off fault light on the miner."""
        try:
            session_id = await self._get_session()
            if session_id:
                await self.api.ledset(session_id, "red", "off")
            return True
        except (APIError, LookupError):
            pass
        return False

    async def restart_backend(self) -> bool:
        """Restart luxminer hashing process.  Wraps [`restart_luxminer`][pyasic.miners.backends.luxminer.LUXMiner.restart_luxminer] to standardize."""
        return await self.restart_luxminer()

    async def restart_luxminer(self) -> bool:
        """Restart luxminer hashing process."""
        try:
            session_id = await self._get_session()
            if session_id:
                await self.api.resetminer(session_id)
            return True
        except (APIError, LookupError):
            pass
        return False

    async def stop_mining(self) -> bool:
        try:
            session_id = await self._get_session()
            if session_id:
                await self.api.curtail(session_id)
            return True
        except (APIError, LookupError):
            pass
        return False

    async def resume_mining(self) -> bool:
        try:
            session_id = await self._get_session()
            if session_id:
                await self.api.wakeup(session_id)
            return True
        except (APIError, LookupError):
            pass

    async def reboot(self) -> bool:
        """Reboots power to the physical miner."""
        try:
            session_id = await self._get_session()
            if session_id:
                await self.api.rebootdevice(session_id)
            return True
        except (APIError, LookupError):
            pass
        return False

    async def get_config(self) -> MinerConfig:
        """Gets the config for the miner and sets it as `self.config`.

        Returns:
            The config from `self.config`.
        """
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        """Configures miner with yaml config."""
        pass

    async def set_power_limit(self, wattage: int) -> bool:
        return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self, api_config: dict = None) -> Optional[str]:
        mac = None
        if not api_config:
            try:
                api_config = await self.api.config()
            except APIError:
                return None

        if api_config:
            try:
                mac = api_config["CONFIG"][0]["MACAddr"]
            except KeyError:
                return None

        return mac

    async def get_model(self) -> Optional[str]:
        if self.model is not None:
            return self.model + " (LuxOS)"
        return "? (LuxOS)"

    async def get_version(self) -> Tuple[Optional[str], Optional[str]]:
        pass

    async def get_api_ver(self) -> Optional[str]:
        pass

    async def get_fw_ver(self) -> Optional[str]:
        pass

    async def get_hostname(self) -> Union[str, None]:
        pass

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return round(float(api_summary["SUMMARY"][0]["GHS 5s"] / 1000), 2)
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def get_hashboards(self, api_stats: dict = None) -> List[HashBoard]:
        hashboards = []

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                board_offset = -1
                boards = api_stats["STATS"]
                if len(boards) > 1:
                    for board_num in range(1, 16, 5):
                        for _b_num in range(5):
                            b = boards[1].get(f"chain_acn{board_num + _b_num}")

                            if b and not b == 0 and board_offset == -1:
                                board_offset = board_num
                    if board_offset == -1:
                        board_offset = 1

                    for i in range(board_offset, board_offset + self.ideal_hashboards):
                        hashboard = HashBoard(
                            slot=i - board_offset, expected_chips=self.nominal_chips
                        )

                        chip_temp = boards[1].get(f"temp{i}")
                        if chip_temp:
                            hashboard.chip_temp = round(chip_temp)

                        temp = boards[1].get(f"temp2_{i}")
                        if temp:
                            hashboard.temp = round(temp)

                        hashrate = boards[1].get(f"chain_rate{i}")
                        if hashrate:
                            hashboard.hashrate = round(float(hashrate) / 1000, 2)

                        chips = boards[1].get(f"chain_acn{i}")
                        if chips:
                            hashboard.chips = chips
                            hashboard.missing = False
                        if (not chips) or (not chips > 0):
                            hashboard.missing = True
                        hashboards.append(hashboard)
            except (IndexError, KeyError, ValueError, TypeError):
                pass

        return hashboards

    async def get_env_temp(self) -> Optional[float]:
        return None

    async def get_wattage(self, api_power: dict) -> Optional[int]:
        if not api_power:
            try:
                api_power = await self.api.power()
            except APIError:
                pass

        if api_power:
            try:
                return api_power["POWER"][0]["Watts"]
            except (IndexError, KeyError, ValueError, TypeError):
                pass

    async def get_wattage_limit(self) -> Optional[int]:
        return None

    async def get_fans(self, api_fans: dict = None) -> List[Fan]:
        if not api_fans:
            try:
                api_fans = await self.api.fans()
            except APIError:
                pass

        fans = []

        if api_fans:
            for fan in range(self.fan_count):
                try:
                    fans.append(Fan(api_fans["FANS"][0]["RPM"]))
                except (IndexError, KeyError, ValueError, TypeError):
                    fans.append(Fan())
        return fans

    async def get_fan_psu(self) -> Optional[int]:
        return None

    async def get_pools(self, api_pools: dict = None) -> List[dict]:
        if not api_pools:
            try:
                api_pools = await self.api.pools()
            except APIError:
                pass

        if api_pools:
            seen = []
            groups = [{"quota": "0"}]
            if api_pools.get("POOLS"):
                for i, pool in enumerate(api_pools["POOLS"]):
                    if len(seen) == 0:
                        seen.append(pool["User"])
                    if not pool["User"] in seen:
                        # need to use get_config, as this will never read perfectly as there are some bad edge cases
                        groups = []
                        cfg = await self.get_config()
                        if cfg:
                            for group in cfg.pool_groups:
                                pools = {"quota": group.quota}
                                for _i, _pool in enumerate(group.pools):
                                    pools[f"pool_{_i + 1}_url"] = _pool.url.replace(
                                        "stratum+tcp://", ""
                                    ).replace("stratum2+tcp://", "")
                                    pools[f"pool_{_i + 1}_user"] = _pool.username
                                groups.append(pools)
                        return groups
                    else:
                        groups[0][f"pool_{i + 1}_url"] = (
                            pool["URL"]
                            .replace("stratum+tcp://", "")
                            .replace("stratum2+tcp://", "")
                        )
                        groups[0][f"pool_{i + 1}_user"] = pool["User"]
            else:
                groups = []
                cfg = await self.get_config()
                if cfg:
                    for group in cfg.pool_groups:
                        pools = {"quota": group.quota}
                        for _i, _pool in enumerate(group.pools):
                            pools[f"pool_{_i + 1}_url"] = _pool.url.replace(
                                "stratum+tcp://", ""
                            ).replace("stratum2+tcp://", "")
                            pools[f"pool_{_i + 1}_user"] = _pool.username
                        groups.append(pools)
                return groups
            return groups

    async def get_errors(self) -> List[MinerErrorData]:
        pass

    async def get_fault_light(self) -> bool:
        pass

    async def get_nominal_hashrate(self, api_stats: dict = None) -> Optional[float]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                ideal_rate = api_stats["STATS"][1]["total_rateideal"]
                try:
                    rate_unit = api_stats["STATS"][1]["rate_unit"]
                except KeyError:
                    rate_unit = "GH"
                if rate_unit == "GH":
                    return round(ideal_rate / 1000, 2)
                if rate_unit == "MH":
                    return round(ideal_rate / 1000000, 2)
                else:
                    return round(ideal_rate, 2)
            except (KeyError, IndexError):
                pass

    async def is_mining(self) -> Optional[bool]:
        pass

    async def get_uptime(self, api_stats: dict = None) -> Optional[int]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            try:
                return int(api_stats["STATS"][1]["Elapsed"])
            except LookupError:
                pass
