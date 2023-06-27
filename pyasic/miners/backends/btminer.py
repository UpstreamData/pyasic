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

import logging
import warnings
from collections import namedtuple
from typing import List, Optional, Tuple

from pyasic.API.btminer import BTMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import MinerErrorData, WhatsminerError
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner

BTMINER_DATA_LOC = {
    "mac": {
        "cmd": "get_mac",
        "kwargs": {
            "api_summary": {"api": "summary"},
            "api_get_miner_info": {"api": "get_miner_info"},
        },
    },
    "model": {"cmd": "get_model", "kwargs": {}},
    "api_ver": {
        "cmd": "get_api_ver",
        "kwargs": {"api_get_version": {"api": "get_version"}},
    },
    "fw_ver": {
        "cmd": "get_fw_ver",
        "kwargs": {
            "api_get_version": {"api": "get_version"},
            "api_summary": {"api": "summary"},
        },
    },
    "hostname": {
        "cmd": "get_hostname",
        "kwargs": {"api_get_miner_info": {"api": "get_miner_info"}},
    },
    "hashrate": {"cmd": "get_hashrate", "kwargs": {"api_summary": {"api": "summary"}}},
    "nominal_hashrate": {
        "cmd": "get_nominal_hashrate",
        "kwargs": {"api_summary": {"api": "summary"}},
    },
    "hashboards": {"cmd": "get_hashboards", "kwargs": {"api_devs": {"api": "devs"}}},
    "env_temp": {"cmd": "get_env_temp", "kwargs": {"api_summary": {"api": "summary"}}},
    "wattage": {"cmd": "get_wattage", "kwargs": {"api_summary": {"api": "summary"}}},
    "wattage_limit": {
        "cmd": "get_wattage_limit",
        "kwargs": {"api_summary": {"api": "summary"}},
    },
    "fans": {
        "cmd": "get_fans",
        "kwargs": {
            "api_summary": {"api": "summary"},
            "api_get_psu": {"api": "get_psu"},
        },
    },
    "fan_psu": {
        "cmd": "get_fan_psu",
        "kwargs": {
            "api_summary": {"api": "summary"},
            "api_get_psu": {"api": "get_psu"},
        },
    },
    "errors": {
        "cmd": "get_errors",
        "kwargs": {
            "api_summary": {"api": "summary"},
            "api_get_error_code": {"api": "get_error_code"},
        },
    },
    "fault_light": {
        "cmd": "get_fault_light",
        "kwargs": {"api_get_miner_info": {"api": "get_miner_info"}},
    },
    "pools": {"cmd": "get_pools", "kwargs": {"api_pools": {"api": "pools"}}},
    "is_mining": {"cmd": "is_mining", "kwargs": {"api_status": {"api": "status"}}},
    "uptime": {
        "cmd": "get_uptime",
        "kwargs": {"api_summary": {"api": "summary"}},
    },
}


class BTMiner(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        # interfaces
        self.api = BTMinerAPI(ip, api_ver)

        # static data
        self.api_type = "BTMiner"
        # data gathering locations
        self.data_locations = BTMINER_DATA_LOC
        # autotuning/shutdown support
        self.supports_shutdown = True

        # data storage
        self.api_ver = api_ver

    async def _reset_api_pwd_to_admin(self, pwd: str):
        try:
            data = await self.api.update_pwd(pwd, "admin")
        except APIError:
            return False
        if data:
            if "Code" in data.keys():
                if data["Code"] == 131:
                    return True
        return False

    async def fault_light_off(self) -> bool:
        try:
            data = await self.api.set_led(auto=True)
        except APIError:
            return False
        if data:
            if "Code" in data.keys():
                if data["Code"] == 131:
                    self.light = False
                    return True
        return False

    async def fault_light_on(self) -> bool:
        try:
            data = await self.api.set_led(auto=False)
            await self.api.set_led(
                auto=False, color="green", start=0, period=1, duration=0
            )
        except APIError:
            return False
        if data:
            if "Code" in data.keys():
                if data["Code"] == 131:
                    self.light = True
                    return True
        return False

    async def reboot(self) -> bool:
        try:
            data = await self.api.reboot()
        except APIError:
            return False
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def restart_backend(self) -> bool:
        try:
            data = await self.api.restart()
        except APIError:
            return False
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def stop_mining(self) -> bool:
        try:
            data = await self.api.power_off(respbefore=True)
        except APIError:
            return False
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def resume_mining(self) -> bool:
        try:
            data = await self.api.power_on()
        except APIError:
            return False
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config

        conf = config.as_wm(user_suffix=user_suffix)
        pools_conf = conf["pools"]

        try:
            await self.api.update_pools(**pools_conf)
        except APIError:
            pass
        try:
            await self.api.adjust_power_limit(conf["wattage"])
        except APIError:
            # cannot set wattage
            pass

    async def get_config(self) -> MinerConfig:
        pools = None
        summary = None
        cfg = MinerConfig()

        try:
            data = await self.api.multicommand("pools", "summary")
            pools = data["pools"][0]
            summary = data["summary"][0]
        except APIError as e:
            logging.warning(e)
        except LookupError:
            pass

        if pools:
            if "POOLS" in pools:
                cfg = cfg.from_api(pools["POOLS"])
        else:
            # somethings wrong with the miner
            warnings.warn(
                f"Failed to gather pool config for miner: {self}, miner did not return pool information."
            )
        if summary:
            if "SUMMARY" in summary:
                if wattage := summary["SUMMARY"][0].get("Power Limit"):
                    cfg.autotuning_wattage = wattage

        self.config = cfg

        return self.config

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            await self.api.adjust_power_limit(wattage)
        except Exception as e:
            logging.warning(f"{self} set_power_limit: {e}")
            return False
        else:
            return True

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(
        self, api_summary: dict = None, api_get_miner_info: dict = None
    ) -> Optional[str]:
        if not api_get_miner_info:
            try:
                api_get_miner_info = await self.api.get_miner_info()
            except APIError:
                pass

        if api_get_miner_info:
            try:
                mac = api_get_miner_info["Msg"]["mac"]
                return str(mac).upper()
            except KeyError:
                pass

        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                mac = api_summary["SUMMARY"][0]["MAC"]
                return str(mac).upper()
            except (KeyError, IndexError):
                pass

    async def get_version(
        self, api_get_version: dict = None, api_summary: dict = None
    ) -> Tuple[Optional[str], Optional[str]]:
        miner_version = namedtuple("MinerVersion", "api_ver fw_ver")
        api_ver = await self.get_api_ver(api_get_version=api_get_version)
        fw_ver = await self.get_fw_ver(
            api_get_version=api_get_version, api_summary=api_summary
        )
        return miner_version(api_ver, fw_ver)

    async def get_api_ver(self, api_get_version: dict = None) -> Optional[str]:
        # Check to see if the version info is already cached
        if self.api_ver:
            return self.api_ver

        if not api_get_version:
            try:
                api_get_version = await self.api.get_version()
            except APIError:
                pass

        if api_get_version:
            if "Code" in api_get_version.keys():
                if api_get_version["Code"] == 131:
                    try:
                        api_ver = api_get_version["Msg"]
                        if not isinstance(api_ver, str):
                            api_ver = api_ver["api_ver"]
                        self.api_ver = api_ver.replace("whatsminer v", "")
                    except (KeyError, TypeError):
                        pass
                    else:
                        self.api.api_ver = self.api_ver
                        return self.api_ver

        return self.api_ver

    async def get_fw_ver(
        self, api_get_version: dict = None, api_summary: dict = None
    ) -> Optional[str]:
        # Check to see if the version info is already cached
        if self.fw_ver:
            return self.fw_ver

        if not api_get_version:
            try:
                api_get_version = await self.api.get_version()
            except APIError:
                pass

        if api_get_version:
            if "Code" in api_get_version.keys():
                if api_get_version["Code"] == 131:
                    try:
                        self.fw_ver = api_get_version["Msg"]["fw_ver"]
                    except (KeyError, TypeError):
                        pass
                    else:
                        return self.fw_ver

        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                self.fw_ver = api_summary["SUMMARY"][0]["Firmware Version"].replace(
                    "'", ""
                )
            except (KeyError, IndexError):
                pass

        return self.fw_ver

    async def get_hostname(self, api_get_miner_info: dict = None) -> Optional[str]:
        hostname = None
        if not api_get_miner_info:
            try:
                api_get_miner_info = await self.api.get_miner_info()
            except APIError:
                return None  # only one way to get this

        if api_get_miner_info:
            try:
                hostname = api_get_miner_info["Msg"]["hostname"]
            except KeyError:
                return None

        return hostname

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return round(float(api_summary["SUMMARY"][0]["MHS 1m"] / 1000000), 2)
            except (KeyError, IndexError):
                pass

    async def get_hashboards(self, api_devs: dict = None) -> List[HashBoard]:

        hashboards = [
            HashBoard(slot=i, expected_chips=self.nominal_chips)
            for i in range(self.ideal_hashboards)
        ]

        if not api_devs:
            try:
                api_devs = await self.api.devs()
            except APIError:
                pass

        if api_devs:
            try:
                for board in api_devs["DEVS"]:
                    if len(hashboards) < board["ASC"] + 1:
                        hashboards.append(
                            HashBoard(
                                slot=board["ASC"], expected_chips=self.nominal_chips
                            )
                        )
                        self.ideal_hashboards += 1
                    hashboards[board["ASC"]].chip_temp = round(board["Chip Temp Avg"])
                    hashboards[board["ASC"]].temp = round(board["Temperature"])
                    hashboards[board["ASC"]].hashrate = round(
                        float(board["MHS 1m"] / 1000000), 2
                    )
                    hashboards[board["ASC"]].chips = board["Effective Chips"]
                    hashboards[board["ASC"]].missing = False
            except (KeyError, IndexError):
                pass

        return hashboards

    async def get_env_temp(self, api_summary: dict = None) -> Optional[float]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return api_summary["SUMMARY"][0]["Env Temp"]
            except (KeyError, IndexError):
                pass

    async def get_wattage(self, api_summary: dict = None) -> Optional[int]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return api_summary["SUMMARY"][0]["Power"]
            except (KeyError, IndexError):
                pass

    async def get_wattage_limit(self, api_summary: dict = None) -> Optional[int]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return api_summary["SUMMARY"][0]["Power Limit"]
            except (KeyError, IndexError):
                pass

    async def get_fans(
        self, api_summary: dict = None, api_get_psu: dict = None
    ) -> List[Fan]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        fans = [Fan() for _ in range(self.fan_count)]
        if api_summary:
            try:
                if self.fan_count > 0:
                    fans = [
                        Fan(api_summary["SUMMARY"][0].get("Fan Speed In", 0)),
                        Fan(api_summary["SUMMARY"][0].get("Fan Speed Out", 0)),
                    ]
            except (KeyError, IndexError):
                pass

        return fans

    async def get_fan_psu(
        self, api_summary: dict = None, api_get_psu: dict = None
    ) -> Optional[int]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return int(api_summary["SUMMARY"][0]["Power Fanspeed"])
            except (KeyError, IndexError):
                pass

        if not api_get_psu:
            try:
                api_get_psu = await self.api.get_psu()
            except APIError:
                pass

        if api_get_psu:
            try:
                return int(api_get_psu["Msg"]["fan_speed"])
            except (KeyError, TypeError):
                pass

    async def get_pools(self, api_pools: dict = None) -> List[dict]:
        groups = []

        if not api_pools:
            try:
                api_pools = await self.api.pools()
            except APIError:
                pass

        if api_pools:
            try:
                pools = {}
                for i, pool in enumerate(api_pools["POOLS"]):
                    pools[f"pool_{i + 1}_url"] = (
                        pool["URL"]
                        .replace("stratum+tcp://", "")
                        .replace("stratum2+tcp://", "")
                    )
                    pools[f"pool_{i + 1}_user"] = pool["User"]
                    pools["quota"] = pool["Quota"] if pool.get("Quota") else "0"

                groups.append(pools)
            except KeyError:
                pass
        return groups

    async def get_errors(
        self, api_summary: dict = None, api_get_error_code: dict = None
    ) -> List[MinerErrorData]:
        errors = []
        if not api_summary and not api_get_error_code:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                for i in range(api_summary["SUMMARY"][0]["Error Code Count"]):
                    err = api_summary["SUMMARY"][0].get(f"Error Code {i}")
                    if err:
                        errors.append(WhatsminerError(error_code=err))
            except (KeyError, IndexError, ValueError, TypeError):
                pass

        if not api_get_error_code:
            try:
                api_get_error_code = await self.api.get_error_code()
            except APIError:
                pass

        if api_get_error_code:
            for err in api_get_error_code["Msg"]["error_code"]:
                if isinstance(err, dict):
                    for code in err:
                        errors.append(WhatsminerError(error_code=int(code)))
                else:
                    errors.append(WhatsminerError(error_code=int(err)))

        return errors

    async def get_nominal_hashrate(self, api_summary: dict = None):
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                nominal_hashrate = api_summary["SUMMARY"][0]["Factory GHS"]
                if nominal_hashrate:
                    return round(nominal_hashrate / 1000, 2)
            except (KeyError, IndexError):
                pass

    async def get_fault_light(self, api_get_miner_info: dict = None) -> bool:
        if not api_get_miner_info:
            try:
                api_get_miner_info = await self.api.get_miner_info()
            except APIError:
                if not self.light:
                    self.light = False

        if api_get_miner_info:
            try:
                self.light = not (api_get_miner_info["Msg"]["ledstat"] == "auto")
            except KeyError:
                pass

        return self.light if self.light else False

    async def set_static_ip(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str = "255.255.255.0",
        hostname: str = None,
    ):
        if not hostname:
            hostname = await self.get_hostname()
        await self.api.net_config(
            ip=ip, mask=subnet_mask, dns=dns, gate=gateway, host=hostname, dhcp=False
        )

    async def set_dhcp(self, hostname: str = None):
        if hostname:
            await self.set_hostname(hostname)
        await self.api.net_config()

    async def set_hostname(self, hostname: str):
        await self.api.set_hostname(hostname)

    async def is_mining(self, api_status: dict = None) -> Optional[bool]:
        if not api_status:
            try:
                api_status = await self.api.status()
            except APIError:
                pass

        if api_status:
            try:
                if api_status["Msg"].get("btmineroff"):
                    try:
                        await self.api.devdetails()
                    except APIError:
                        return False
                    return True
                return True if api_status["Msg"]["mineroff"] == "false" else False
            except LookupError:
                pass

    async def get_uptime(self, api_summary: dict = None) -> Optional[int]:
        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                return int(api_summary["SUMMARY"][0]["Elapsed"])
            except LookupError:
                pass
