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
from typing import Union, List


from pyasic.API.btminer import BTMinerAPI
from pyasic.miners.base import BaseMiner
from pyasic.errors import APIError

from pyasic.data import MinerData, HashBoard
from pyasic.data.error_codes import WhatsminerError, MinerErrorData
from pyasic.config import MinerConfig

from pyasic.settings import PyasicSettings


class BTMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BTMinerAPI(ip)
        self.api_type = "BTMiner"

    async def get_model(self) -> Union[str, None]:
        """Get miner model.

        Returns:
            Miner model or None.
        """
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model
        version_data = await self.api.devdetails()
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].split("V")[0]
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_hostname(self) -> Union[str, None]:
        """Get miner hostname.

        Returns:
            The hostname of the miner as a string or None.
        """
        if self.hostname:
            return self.hostname
        try:
            host_data = await self.api.get_miner_info()
            if host_data:
                host = host_data["Msg"]["hostname"]
                logging.debug(f"Found hostname for {self.ip}: {host}")
                self.hostname = host
                return self.hostname
        except APIError:
            logging.info(f"Failed to get hostname for miner: {self}")
            return None
        except Exception:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return None

    async def get_mac(self) -> str:
        """Get the mac address of the miner.

        Returns:
            The mac address of the miner as a string.
        """
        mac = ""
        data = await self.api.summary()
        if data:
            if data.get("SUMMARY"):
                if len(data["SUMMARY"]) > 0:
                    _mac = data["SUMMARY"][0].get("MAC")
                    if _mac:
                        mac = _mac
        if mac == "":
            try:
                data = await self.api.get_miner_info()
                if data:
                    if "Msg" in data.keys():
                        if "mac" in data["Msg"].keys():
                            mac = data["Msg"]["mac"]
            except APIError:
                pass

        return str(mac).upper()

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

    async def check_light(self) -> bool:
        data = None

        try:
            data = await self.api.get_miner_info()
        except APIError:
            if not self.light:
                self.light = False
        if data:
            if "Msg" in data.keys():
                if "ledstat" in data["Msg"].keys():
                    if not data["Msg"]["ledstat"] == "auto":
                        self.light = True
                    if data["Msg"]["ledstat"] == "auto":
                        self.light = False
        return self.light

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

    async def get_errors(self) -> List[MinerErrorData]:
        data = []
        try:
            err_data = await self.api.get_error_code()
            if err_data:
                if err_data.get("Msg"):
                    if err_data["Msg"].get("error_code"):
                        for err in err_data["Msg"]["error_code"]:
                            if isinstance(err, dict):
                                for code in err:
                                    data.append(WhatsminerError(error_code=int(code)))
                            else:
                                data.append(WhatsminerError(error_code=int(err)))
        except APIError:
            summary_data = await self.api.summary()
            if summary_data.get("SUMMARY"):
                summary_data = summary_data["SUMMARY"]
                if summary_data[0].get("Error Code Count"):
                    for i in range(summary_data[0]["Error Code Count"]):
                        if summary_data[0].get(f"Error Code {i}"):
                            if not summary_data[0][f"Error Code {i}"] == "":
                                data.append(
                                    WhatsminerError(
                                        error_code=summary_data[0][f"Error Code {i}"]
                                    )
                                )

        return data

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
        data = await self.api.power_off(respbefore=True)
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def resume_mining(self) -> bool:
        data = await self.api.power_on()
        if data.get("Msg"):
            if data["Msg"] == "API command OK":
                return True
        return False

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        conf = config.as_wm(user_suffix=user_suffix)

        await self.api.update_pools(
            conf[0]["url"],
            conf[0]["user"],
            conf[0]["pass"],
            conf[1]["url"],
            conf[1]["user"],
            conf[1]["pass"],
            conf[2]["url"],
            conf[2]["user"],
            conf[2]["pass"],
        )

    async def get_config(self) -> MinerConfig:
        pools = None
        cfg = MinerConfig()

        try:
            pools = await self.api.pools()
        except APIError as e:
            logging.warning(e)

        if pools:
            if "POOLS" in pools.keys():
                cfg = cfg.from_api(pools["POOLS"])
        return cfg

    async def get_data(self, allow_warning: bool = True) -> MinerData:
        """Get data from the miner.

        Returns:
            A [`MinerData`][pyasic.data.MinerData] instance containing the miners data.
        """
        data = MinerData(
            ip=str(self.ip),
            ideal_chips=self.nominal_chips * self.ideal_hashboards,
            ideal_hashboards=self.ideal_hashboards,
        )

        mac = None

        try:
            model = await self.get_model()
        except APIError:
            logging.info(f"Failed to get model: {self}")
            model = None
            data.model = "Whatsminer"

        try:
            hostname = await self.get_hostname()
        except APIError:
            logging.info(f"Failed to get hostname: {self}")
            hostname = None
            data.hostname = "Whatsminer"

        if model:
            data.model = model

        if hostname:
            data.hostname = hostname

        data.fault_light = await self.check_light()

        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            try:
                miner_data = await self.api.multicommand("summary", "devs", "pools", allow_warning=allow_warning)
                if miner_data:
                    break
            except APIError:
                pass
        if not miner_data:
            return data

        summary = miner_data.get("summary")[0]
        devs = miner_data.get("devs")[0]
        pools = miner_data.get("pools")[0]
        try:
            psu_data = await self.api.get_psu()
        except APIError:
            psu_data = None
        try:
            err_data = await self.api.get_error_code()
        except APIError:
            err_data = None

        if summary:
            summary_data = summary.get("SUMMARY")
            if summary_data:
                if len(summary_data) > 0:
                    wattage_limit = None
                    if summary_data[0].get("MAC"):
                        mac = summary_data[0]["MAC"]

                    if summary_data[0].get("Env Temp"):
                        data.env_temp = summary_data[0]["Env Temp"]

                    if summary_data[0].get("Power Limit"):
                        wattage_limit = summary_data[0]["Power Limit"]

                    if summary_data[0].get("Power Fanspeed"):
                        data.fan_psu = summary_data[0]["Power Fanspeed"]

                    data.fan_1 = summary_data[0]["Fan Speed In"]
                    data.fan_2 = summary_data[0]["Fan Speed Out"]

                    hr = summary_data[0].get("MHS 1m")
                    if hr:
                        data.hashrate = round(hr / 1000000, 2)

                    wattage = summary_data[0].get("Power")
                    if wattage:
                        data.wattage = round(wattage)

                        if not wattage_limit:
                            wattage_limit = round(wattage)

                    data.wattage_limit = wattage_limit

                    if summary_data[0].get("Error Code Count"):
                        for i in range(summary_data[0]["Error Code Count"]):
                            if summary_data[0].get(f"Error Code {i}"):
                                if not summary_data[0][f"Error Code {i}"] == "":
                                    data.errors.append(
                                        WhatsminerError(
                                            error_code=summary_data[0][
                                                f"Error Code {i}"
                                            ]
                                        )
                                    )

        if psu_data:
            psu = psu_data.get("Msg")
            if psu:
                if psu.get("fan_speed"):
                    data.fan_psu = psu["fan_speed"]

        if err_data:
            if err_data.get("Msg"):
                if err_data["Msg"].get("error_code"):
                    for err in err_data["Msg"]["error_code"]:
                        if isinstance(err, dict):
                            for code in err:
                                data.errors.append(
                                    WhatsminerError(error_code=int(code))
                                )
                        else:
                            data.errors.append(WhatsminerError(error_code=int(err)))

        if devs:
            dev_data = devs.get("DEVS")
            if dev_data:
                for board in dev_data:
                    temp_board = HashBoard(
                        slot=board["ASC"],
                        chip_temp=round(board["Chip Temp Avg"]),
                        temp=round(board["Temperature"]),
                        hashrate=round(board["MHS 1m"] / 1000000, 2),
                        chips=board["Effective Chips"],
                        missing=False if board["Effective Chips"] > 0 else True,
                        expected_chips=self.nominal_chips,
                    )
                    data.hashboards.append(temp_board)

        if pools:
            pool_1 = None
            pool_2 = None
            pool_1_user = None
            pool_2_user = None
            pool_1_quota = 1
            pool_2_quota = 1
            quota = 0
            for pool in pools.get("POOLS"):
                if not pool_1_user:
                    pool_1_user = pool.get("User")
                    pool_1 = pool["URL"]
                    pool_1_quota = pool["Quota"]
                elif not pool_2_user:
                    pool_2_user = pool.get("User")
                    pool_2 = pool["URL"]
                    pool_2_quota = pool["Quota"]
                if not pool.get("User") == pool_1_user:
                    if not pool_2_user == pool.get("User"):
                        pool_2_user = pool.get("User")
                        pool_2 = pool["URL"]
                        pool_2_quota = pool["Quota"]
            if pool_2_user and not pool_2_user == pool_1_user:
                quota = f"{pool_1_quota}/{pool_2_quota}"

            if pool_1:
                pool_1 = pool_1.replace("stratum+tcp://", "").replace(
                    "stratum2+tcp://", ""
                )
                data.pool_1_url = pool_1

            if pool_1_user:
                data.pool_1_user = pool_1_user

            if pool_2:
                pool_2 = pool_2.replace("stratum+tcp://", "").replace(
                    "stratum2+tcp://", ""
                )
                data.pool_2_url = pool_2

            if pool_2_user:
                data.pool_2_user = pool_2_user

            if quota:
                data.pool_split = str(quota)

        if not mac:
            try:
                mac = await self.get_mac()
            except APIError:
                logging.info(f"Failed to get mac: {self}")
                mac = None

        if mac:
            data.mac = mac

        return data
