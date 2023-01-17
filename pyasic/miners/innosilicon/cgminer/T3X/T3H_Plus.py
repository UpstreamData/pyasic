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
import json
import logging
import warnings
from typing import List, Union, Optional, Tuple
from collections import namedtuple

import httpx

from pyasic.config import MinerConfig
from pyasic.data import HashBoard
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
        self, web_all_data: dict = None, web_overview: dict = None
    ) -> Optional[str]:
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
        self, api_summary: dict = None, web_all_data: dict = None
    ) -> Optional[float]:
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
        self, api_stats: dict = None, web_all_data: dict = None
    ) -> List[HashBoard]:
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

    async def get_wattage(self, web_all_data: dict = None) -> Optional[int]:
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
        self, web_all_data: dict = None
    ) -> Tuple[
        Tuple[Optional[int], Optional[int], Optional[int], Optional[int]],
        Tuple[Optional[int]],
    ]:
        fan_speeds = namedtuple("FanSpeeds", "fan_1 fan_2 fan_3 fan_4")
        psu_fan_speeds = namedtuple("PSUFanSpeeds", "psu_fan")
        miner_fan_speeds = namedtuple("MinerFans", "fan_speeds psu_fan_speeds")

        fans = fan_speeds(None, None, None, None)
        psu_fans = psu_fan_speeds(None)

        if not web_all_data:
            try:
                web_all_data = await self.send_web_command("getAll")
            except APIError:
                pass
            else:
                web_all_data = web_all_data["all"]

        if web_all_data:
            try:
                spd = web_all_data["fansSpeed"]
            except KeyError:
                pass
            else:
                f = [None, None, None, None]
                round((int(spd) * 6000) / 100)
                for i in range(self.fan_count):
                    f[i] = spd
                fans = fan_speeds(*f)

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

    async def get_errors(self, web_error_details: dict = None) -> List[MinerErrorData]:
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

    async def _get_data(self, allow_warning: bool) -> dict:
        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            try:
                miner_data = await self.api.multicommand(
                    "summary",
                    "version",
                    "pools",
                    "stats",
                    allow_warning=allow_warning,
                )
            except APIError:
                pass
            if miner_data:
                break
        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            try:
                miner_data = await self.api.multicommand(
                    "summary",
                    "pools",
                    "version",
                    "devdetails",
                    "stats",
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
            pools = miner_data.get("pools")
            if pools:
                pools = pools[0]
            version = miner_data.get("version")
            if version:
                version = version[0]
            stats = miner_data.get("stats")
            if stats:
                stats = stats[0]
        else:
            summary, pools, version, stats = (None for _ in range(4))

        try:
            web_all_data = await self.send_web_command("getAll")
        except APIError:
            web_all_data = None
        try:
            web_type = await self.send_web_command("type")
        except APIError:
            web_type = None
        try:
            web_error_details = await self.send_web_command("getErrorDetail")
        except APIError:
            web_error_details = None

        data = {  # noqa - Ignore dictionary could be re-written
            # ip - Done at start
            # datetime - Done auto
            "mac": await self.get_mac(web_all_data=web_all_data),
            "model": await self.get_model(web_type=web_type),
            # make - Done at start
            "api_ver": None,  # - Done at end
            "fw_ver": None,  # - Done at end
            "hostname": await self.get_hostname(),
            "hashrate": await self.get_hashrate(
                api_summary=summary, web_all_data=web_all_data
            ),
            "hashboards": await self.get_hashboards(
                api_stats=stats, web_all_data=web_all_data
            ),
            # ideal_hashboards - Done at start
            "env_temp": await self.get_env_temp(),
            "wattage": await self.get_wattage(web_all_data=web_all_data),
            "wattage_limit": await self.get_wattage_limit(),
            "fan_1": None,  # - Done at end
            "fan_2": None,  # - Done at end
            "fan_3": None,  # - Done at end
            "fan_4": None,  # - Done at end
            "fan_psu": None,  # - Done at end
            # ideal_chips - Done at start
            "pool_split": None,  # - Done at end
            "pool_1_url": None,  # - Done at end
            "pool_1_user": None,  # - Done at end
            "pool_2_url": None,  # - Done at end
            "pool_2_user": None,  # - Done at end
            "errors": await self.get_errors(web_error_details=web_error_details),
            "fault_light": await self.get_fault_light(),
        }

        data["api_ver"], data["fw_ver"] = await self.get_version(api_version=version)
        fan_data = await self.get_fans(web_all_data=web_all_data)

        if fan_data:
            data["fan_1"] = fan_data.fan_speeds.fan_1  # noqa
            data["fan_2"] = fan_data.fan_speeds.fan_2  # noqa
            data["fan_3"] = fan_data.fan_speeds.fan_3  # noqa
            data["fan_4"] = fan_data.fan_speeds.fan_4  # noqa

            data["fan_psu"] = fan_data.psu_fan_speeds.psu_fan  # noqa

        pools_data = await self.get_pools(api_pools=pools)

        if pools_data:
            data["pool_1_url"] = pools_data[0]["pool_1_url"]
            data["pool_1_user"] = pools_data[0]["pool_1_user"]
            if len(pools_data) > 1:
                data["pool_2_url"] = pools_data[1]["pool_2_url"]
                data["pool_2_user"] = pools_data[1]["pool_2_user"]
                data["pool_split"] = f"{pools_data[0]['quota']}/{pools_data[1]['quota']}"
            else:
                try:
                    data["pool_2_url"] = pools_data[0]["pool_2_url"]
                    data["pool_2_user"] = pools_data[0]["pool_2_user"]
                    data["quota"] = "0"
                except KeyError:
                    pass

        return data
