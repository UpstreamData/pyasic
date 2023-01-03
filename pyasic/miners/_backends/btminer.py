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

import ipaddress
import logging
from typing import List, Union, Tuple, Optional
from collections import namedtuple

from pyasic.API.btminer import BTMinerAPI
from pyasic.config import MinerConfig
from pyasic.data import HashBoard, MinerData
from pyasic.data.error_codes import MinerErrorData, WhatsminerError
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.settings import PyasicSettings


class BTMiner(BaseMiner):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BTMinerAPI(ip, api_ver)
        self.api_type = "BTMiner"
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
        data = await self.api.reboot()
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def restart_backend(self) -> bool:
        data = await self.api.restart()
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
        conf = config.as_wm(user_suffix=user_suffix)
        pools_conf = conf["pools"]

        await self.api.update_pools(
            pools_conf[0]["url"],
            pools_conf[0]["user"],
            pools_conf[0]["pass"],
            pools_conf[1]["url"],
            pools_conf[1]["user"],
            pools_conf[1]["pass"],
            pools_conf[2]["url"],
            pools_conf[2]["user"],
            pools_conf[2]["pass"],
        )
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

        if pools:
            if "POOLS" in pools:
                cfg = cfg.from_api(pools["POOLS"])
        if summary:
            if "SUMMARY" in summary:
                if wattage := summary["SUMMARY"][0].get("Power Limit"):
                    cfg.autotuning_wattage = wattage

        return cfg

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
        self, api_summary: dict = None, api_miner_info: dict = None
    ) -> Optional[str]:
        if not api_miner_info:
            try:
                api_miner_info = await self.api.get_miner_info()
            except APIError:
                pass

        if api_miner_info:
            try:
                mac = api_miner_info["Msg"]["mac"]
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

    async def get_model(self, api_devdetails: dict = None) -> Optional[str]:
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        if not api_devdetails:
            try:
                api_devdetails = await self.api.devdetails()
            except APIError:
                pass

        if api_devdetails:
            try:
                self.model = api_devdetails["DEVDETAILS"][0]["Model"].split("V")[0]
                logging.debug(f"Found model for {self.ip}: {self.model}")
                return self.model
            except (TypeError, IndexError, KeyError):
                pass

        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_version(
        self, api_version: dict = None
    ) -> Tuple[Optional[str], Optional[str]]:
        # check if version is cached
        miner_version = namedtuple("MinerVersion", "api_ver fw_ver")
        # Check to see if the version info is already cached
        if self.api_ver and self.fw_ver:
            return miner_version(self.api_ver, self.fw_ver)

        if not api_version:
            try:
                api_version = await self.api.get_version()
            except APIError:
                pass

        if api_version:
            if "Code" in api_version.keys():
                if api_version["Code"] == 131:
                    self.api_ver = api_version["Msg"]["api_ver"].replace(
                        "whatsminer v", ""
                    )
                    self.fw_ver = api_version["Msg"]["fw_ver"]
                self.api.api_ver = self.api_ver

        return miner_version(self.api_ver, self.fw_ver)

    async def get_hostname(self, api_miner_info: dict = None) -> Optional[str]:
        if self.hostname:
            return self.hostname

        if not api_miner_info:
            try:
                api_miner_info = await self.api.get_miner_info()
            except APIError:
                return None  # only one way to get this

        if api_miner_info:
            try:
                self.hostname = api_miner_info["Msg"]["hostname"]
            except KeyError:
                return None

        return self.hostname

    async def get_hashrate(self, api_summary: dict = None) -> Optional[float]:
        # get hr from API
        if not api_summary:
            api_summary = await self.api.summary()

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
                    hashboards[board["ASC"]].chip_temp = round(board["Chip Temp Avg"])
                    hashboards[board["ASC"]].temp = round(board["Temperature"])
                    hashboards[board["ASC"]].hashrate = round(
                        float(board["MHS 1m"] / 1000000), 2
                    )
                    hashboards[board["ASC"]].chips = board["Effective Chips"]
                    hashboards[board["ASC"]].missing = False
            except KeyError:
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
        self, api_summary: dict = None, api_psu: dict = None
    ) -> Tuple[
        Tuple[Optional[int], Optional[int], Optional[int], Optional[int]],
        Tuple[Optional[int]],
    ]:
        fan_speeds = namedtuple("FanSpeeds", "fan_1 fan_2 fan_3 fan_4")
        psu_fan_speeds = namedtuple("PSUFanSpeeds", "psu_fan")
        miner_fan_speeds = namedtuple("MinerFans", "fan_speeds psu_fan_speeds")

        fans = fan_speeds(None, None, None, None)
        psu_fans = psu_fan_speeds(None)

        if not api_summary:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                if self.fan_count > 0:
                    fans = fan_speeds(
                        api_summary["SUMMARY"][0]["Fan Speed In"],
                        api_summary["SUMMARY"][0]["Fan Speed Out"],
                        None,
                        None,
                    )
                    psu_fans = psu_fan_speeds(int(api_summary["SUMMARY"][0]["Power Fanspeed"]))
            except (KeyError, IndexError):
                pass

        if not psu_fans[0]:
            if not api_psu:
                try:
                    api_psu = await self.api.get_psu()
                except APIError:
                    pass

            if api_psu:
                try:
                    psu_fans = psu_fan_speeds(int(api_psu["Msg"]["fan_speed"]))
                except (KeyError, TypeError):
                    pass

        return miner_fan_speeds(fans, psu_fans)

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
        self, api_summary: dict = None, api_error_codes: dict = None
    ) -> List[MinerErrorData]:
        errors = []
        if not api_summary and not api_error_codes:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if api_summary:
            try:
                for i in range(api_summary["SUMMARY"][0]["Error Code Count"]):
                    errors.append(
                        WhatsminerError(error_code=api_summary["SUMMARY"][0][f"Error Code {i}"])
                    )

            except (KeyError, IndexError, ValueError, TypeError):
                pass

        if not api_error_codes:
            try:
                api_error_codes = await self.api.get_error_code()
            except APIError:
                pass

        if api_error_codes:
            for err in api_error_codes["Msg"]["error_code"]:
                if isinstance(err, dict):
                    for code in err:
                        errors.append(WhatsminerError(error_code=int(code)))
                else:
                    errors.append(WhatsminerError(error_code=int(err)))

        return errors

    async def get_fault_light(self, api_miner_info: dict = None) -> bool:
        data = None

        if not api_miner_info:
            try:
                api_miner_info = await self.api.get_miner_info()
            except APIError:
                if not self.light:
                    self.light = False

        if api_miner_info:
            try:
                self.light = api_miner_info["Msg"]["ledstat"] == "auto"
            except KeyError:
                pass

        return self.light if self.light else False

    async def _get_data(self, allow_warning: bool) -> dict:
        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            try:
                miner_data = await self.api.multicommand(
                    "summary",
                    "get_version",
                    "pools",
                    "devdetails",
                    "devs",
                    "get_psu",
                    "get_miner_info",
                    "get_error_code",
                    allow_warning=allow_warning,
                )
            except APIError:
                pass
            if miner_data:
                break
        if miner_data:
            summary = miner_data.get("summary")
            if summary:
                summary = summary[0]
            version = miner_data.get("get_version")
            if version:
                version = version[0]
            pools = miner_data.get("pools")
            if pools:
                pools = pools[0]
            devdetails = miner_data.get("devdetails")
            if devdetails:
                devdetails = devdetails[0]
            devs = miner_data.get("devs")
            if devs:
                devs = devs[0]
            psu = miner_data.get("get_psu")
            if psu:
                psu = psu[0]
            miner_info = miner_data.get("get_miner_info")
            if miner_info:
                miner_info = miner_info[0]
            error_codes = miner_data.get("get_error_codes")
            if error_codes:
                error_codes = error_codes[0]
        else:
            summary, version, pools, devdetails, devs, psu, miner_info, error_codes  = (None for _ in range(8))




        data = {  # noqa - Ignore dictionary could be re-written
            # ip - Done at start
            # datetime - Done auto
            "mac": await self.get_mac(api_summary=summary, api_miner_info=miner_info),
            "model": await self.get_model(api_devdetails=devdetails),
            # make - Done at start
            # api_ver - Done at end
            # fw_ver - Done at end
            "hostname": await self.get_hostname(api_miner_info=miner_info),
            "hashrate": await self.get_hashrate(
                api_summary=summary
            ),
            "hashboards": await self.get_hashboards(
                api_devs=devs
            ),
            # ideal_hashboards - Done at start
            "env_temp": await self.get_env_temp(api_summary=summary),
            "wattage": await self.get_wattage(
                api_summary=summary
            ),
            "wattage_limit": await self.get_wattage_limit(
                api_summary=summary
            ),
            # fan_1 - Done at end
            # fan_2 - Done at end
            # fan_3 - Done at end
            # fan_4 - Done at end
            # fan_psu - Done at end
            # ideal_chips - Done at start
            # pool_split - Done at end
            # pool_1_url - Done at end
            # pool_1_user - Done at end
            # pool_2_url - Done at end
            # pool_2_user - Done at end`
            "errors": await self.get_errors(
                api_summary=summary, api_error_codes=error_codes
            ),
            "fault_light": await self.get_fault_light(api_miner_info=miner_info),
        }

        data["api_ver"], data["fw_ver"] = await self.get_version(
            api_version=version
        )
        fan_data = await self.get_fans()

        data["fan_1"] = fan_data.fan_speeds.fan_1 # noqa
        data["fan_2"] = fan_data.fan_speeds.fan_2 # noqa
        data["fan_3"] = fan_data.fan_speeds.fan_3 # noqa
        data["fan_4"] = fan_data.fan_speeds.fan_4 # noqa

        data["fan_psu"] = fan_data.psu_fan_speeds.psu_fan # noqa

        pools_data = await self.get_pools(api_pools=pools)
        data["pool_1_url"] = pools_data[0]["pool_1_url"]
        data["pool_1_user"] = pools_data[0]["pool_1_user"]
        if len(pools_data) > 1:
            data["pool_2_url"] = pools_data[1]["pool_1_url"]
            data["pool_2_user"] = pools_data[1]["pool_1_user"]
            data["pool_split"] = f"{pools_data[0]['quota']}/{pools_data[1]['quota']}"
        else:
            try:
                data["pool_2_url"] = pools_data[0]["pool_1_url"]
                data["pool_2_user"] = pools_data[0]["pool_1_user"]
                data["quota"] = "0"
            except KeyError:
                pass

        return data
