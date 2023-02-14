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
import json
import logging
import warnings
from collections import namedtuple
from typing import List, Optional, Tuple, Union

import httpx

from pyasic.config import MinerConfig
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import InnosiliconError, MinerErrorData
from pyasic.errors import APIError
from pyasic.miners._backends import CGMiner  # noqa - Ignore access to _module
from pyasic.miners._types import InnosiliconT3HPlus  # noqa - Ignore access to _module
from pyasic.settings import PyasicSettings


class CGMinerInnosiliconT3HPlus(CGMiner, InnosiliconT3HPlus):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.uname = "admin"
        self.pwd = PyasicSettings().global_innosilicon_password
        self.jwt = None

    async def auth(self):
        async with httpx.AsyncClient() as client:
            try:
                auth = await client.post(
                    f"http://{self.ip}/api/auth",
                    data={"username": self.uname, "password": self.pwd},
                )
            except httpx.HTTPError:
                warnings.warn(f"Could not authenticate web token with miner: {self}")
            else:
                json_auth = auth.json()
                self.jwt = json_auth.get("jwt")
            return self.jwt

    async def send_web_command(self, command: str, data: Union[dict, None] = None):
        if not self.jwt:
            await self.auth()
        if not data:
            data = {}
        async with httpx.AsyncClient() as client:
            for i in range(PyasicSettings().miner_get_data_retries):
                try:
                    response = await client.post(
                        f"http://{self.ip}/api/{command}",
                        headers={"Authorization": "Bearer " + self.jwt},
                        timeout=5,
                        data=data,
                    )
                    json_data = response.json()
                    if (
                        not json_data.get("success")
                        and "token" in json_data
                        and json_data.get("token") == "expired"
                    ):
                        # refresh the token, retry
                        await self.auth()
                        continue
                    if not json_data.get("success"):
                        if json_data.get("msg"):
                            raise APIError(json_data["msg"])
                        elif json_data.get("message"):
                            raise APIError(json_data["message"])
                        raise APIError("Innosilicon web api command failed.")
                    return json_data
                except httpx.HTTPError:
                    pass
                except json.JSONDecodeError:
                    pass

    async def fault_light_on(self) -> bool:
        return False

    async def fault_light_off(self) -> bool:
        return False

    async def get_config(self, api_pools: dict = None) -> MinerConfig:
        if not api_pools:
            try:
                api_pools = await self.api.pools()
            except APIError as e:
                logging.warning(e)

        if api_pools:
            if "POOLS" in api_pools.keys():
                cfg = MinerConfig().from_api(api_pools["POOLS"])
                self.config = cfg
        return self.config

    async def reboot(self) -> bool:
        try:
            data = await self.send_web_command("reboot")
        except APIError:
            pass
        else:
            return data["success"]

    async def restart_cgminer(self) -> bool:
        try:
            data = await self.send_web_command("restartCgMiner")
        except APIError:
            pass
        else:
            return data["success"]

    async def restart_backend(self) -> bool:
        return await self.restart_cgminer()

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        await self.send_web_command(
            "updatePools", data=config.as_inno(user_suffix=user_suffix)
        )

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(
        self,
        web_getAll: dict = None,
        web_overview: dict = None,  # noqa: named this way for automatic functionality
    ) -> Optional[str]:
        web_all_data = web_getAll
        if not web_all_data and not web_overview:
            try:
                web_overview = await self.send_web_command("overview")
            except APIError:
                pass

        if web_all_data:
            try:
                mac = web_all_data["mac"]
                return mac.upper()
            except KeyError:
                pass

        if web_overview:
            try:
                mac = web_overview["version"]["ethaddr"]
                return mac.upper()
            except KeyError:
                pass

    async def get_model(self, web_type: dict = None) -> Optional[str]:
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        if not web_type:
            try:
                web_type = await self.send_web_command("type")
            except APIError:
                pass

        if web_type:
            try:
                self.model = web_type["type"]
                return self.model
            except KeyError:
                pass

    async def get_hashrate(
        self,
        api_summary: dict = None,
        web_getAll: dict = None,  # noqa: named this way for automatic functionality
    ) -> Optional[float]:
        web_all_data = web_getAll
        if not api_summary and not web_all_data:
            try:
                api_summary = await self.api.summary()
            except APIError:
                pass

        if web_all_data:
            try:
                return round(
                    float(web_all_data["total_hash"]["Hash Rate H"] / 1000000000000), 2
                )
            except KeyError:
                pass

        if api_summary:
            try:
                return round(float(api_summary["SUMMARY"][0]["MHS 1m"] / 1000000), 2)
            except (KeyError, IndexError):
                pass

    async def get_hashboards(
        self,
        api_stats: dict = None,
        web_getAll: dict = None,  # noqa: named this way for automatic functionality
    ) -> List[HashBoard]:
        web_all_data = web_getAll
        hashboards = [
            HashBoard(slot=i, expected_chips=self.nominal_chips)
            for i in range(self.ideal_hashboards)
        ]

        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if not web_all_data:
            try:
                web_all_data = await self.send_web_command("getAll")
            except APIError:
                pass
            else:
                web_all_data = web_all_data["all"]

        if api_stats:
            if api_stats.get("STATS"):
                for idx, board in enumerate(api_stats["STATS"]):
                    try:
                        chips = board["Num active chips"]
                    except KeyError:
                        pass
                    else:
                        hashboards[idx].chips = chips
                        hashboards[idx].missing = False

        if web_all_data:
            if web_all_data.get("chain"):
                for idx, board in enumerate(web_all_data["chain"]):
                    temp = board.get("Temp min")
                    if temp:
                        hashboards[idx].temp = round(temp)

                    hashrate = board.get("Hash Rate H")
                    if hashrate:
                        hashboards[idx].hashrate = round(hashrate / 1000000000000, 2)

                    chip_temp = board.get("Temp max")
                    if chip_temp:
                        hashboards[idx].chip_temp = round(chip_temp)

        return hashboards

    async def get_wattage(
        self, web_getAll: dict = None
    ) -> Optional[int]:  # noqa: named this way for automatic functionality
        web_all_data = web_getAll
        if not web_all_data:
            try:
                web_all_data = await self.send_web_command("getAll")
            except APIError:
                pass
            else:
                web_all_data = web_all_data["all"]

        if web_all_data:
            try:
                return web_all_data["power"]
            except KeyError:
                pass

    async def get_fans(
        self,
        web_getAll: dict = None,  # noqa: named this way for automatic functionality
    ) -> List[Fan]:
        web_all_data = web_getAll
        if not web_all_data:
            try:
                web_all_data = await self.send_web_command("getAll")
            except APIError:
                pass
            else:
                web_all_data = web_all_data["all"]

        fan_data = [Fan(), Fan(), Fan(), Fan()]
        if web_all_data:
            try:
                spd = web_all_data["fansSpeed"]
            except KeyError:
                pass
            else:
                round((int(spd) * 6000) / 100)
                for i in range(self.fan_count):
                    fan_data[i] = Fan(spd)

        return fan_data

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
        self, web_getErrorDetail: dict = None
    ) -> List[MinerErrorData]:  # noqa: named this way for automatic functionality
        web_error_details = web_getErrorDetail
        errors = []
        if not web_error_details:
            try:
                web_error_details = await self.send_web_command("getErrorDetail")
            except APIError:
                pass

        if web_error_details:
            try:
                # only 1 error?
                # TODO: check if this should be a loop, can't remember.
                err = web_error_details["code"]
            except KeyError:
                pass
            else:
                err = int(err)
                if not err == 0:
                    errors.append(InnosiliconError(error_code=err))
        return errors
