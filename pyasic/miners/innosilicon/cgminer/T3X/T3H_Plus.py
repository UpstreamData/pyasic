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

from pyasic.miners._backends import CGMiner  # noqa - Ignore access to _module
from pyasic.miners._types import InnosiliconT3HPlus  # noqa - Ignore access to _module
from pyasic.data import MinerData, HashBoard
from pyasic.data.error_codes import InnosiliconError, MinerErrorData
from pyasic.settings import PyasicSettings
from pyasic.config import MinerConfig
from pyasic.errors import APIError

import httpx
import warnings
from typing import Union, List
import logging


class CGMinerInnosiliconT3HPlus(CGMiner, InnosiliconT3HPlus):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
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
            except Exception:
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

    async def fault_light_on(self) -> bool:
        return False

    async def fault_light_off(self) -> bool:
        return False

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

    async def get_mac(self) -> Union[str, None]:
        try:
            data = await self.send_web_command("overview")
        except APIError:
            pass
        else:
            if data.get("version"):
                return data["version"].get("ethaddr").upper()

    async def get_hostname(self) -> Union[str, None]:
        return None

    async def get_model(self) -> Union[str, None]:
        try:
            data = await self.send_web_command("type")
        except APIError:
            pass
        else:
            return data["type"]

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

    async def get_errors(self) -> List[MinerErrorData]:
        errors = []
        try:
            data = await self.send_web_command("getErrorDetail")
        except APIError:
            pass
        else:
            if "code" in data:
                err = data["code"]
                if isinstance(err, str):
                    err = int(err)
                if not err == 0:
                    errors.append(InnosiliconError(error_code=err))
        return errors

    async def get_data(self, allow_warning: bool = False) -> MinerData:
        data = MinerData(
            ip=str(self.ip),
            ideal_chips=self.nominal_chips * self.ideal_hashboards,
            ideal_hashboards=self.ideal_hashboards,
            hashboards=[
                HashBoard(slot=i, expected_chips=self.nominal_chips)
                for i in range(self.ideal_hashboards)
            ],
        )

        board_offset = -1
        fan_offset = -1

        model = await self.get_model()
        hostname = await self.get_hostname()

        if model:
            data.model = model

        if hostname:
            data.hostname = hostname

        data.errors = await self.get_errors()
        data.fault_light = await self.check_light()

        miner_data = None
        all_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            miner_data = await self.api.multicommand(
                "summary", "pools", "stats", allow_warning=allow_warning
            )

            if miner_data:
                break

        try:
            all_data = (await self.send_web_command("getAll"))["all"]
        except APIError:
            pass

        if not (miner_data or all_data):
            return data

        summary = miner_data.get("summary")
        pools = miner_data.get("pools")
        stats = miner_data.get("stats")

        if summary:
            summary = summary[0]
            hr = summary.get("SUMMARY")
            if hr:
                if len(hr) > 0:
                    hr = hr[0].get("MHS 1m")
                    if hr:
                        data.hashrate = round(hr / 1000000, 2)
        elif all_data:
            if all_data.get("total_hash"):
                print(all_data["total_hash"])
                hr = all_data["total_hash"].get("Hash Rate H")
                if hr:
                    data.hashrate = round(hr / 1000000000000, 2)

        if stats:
            stats = stats[0]
            if stats.get("STATS"):
                for idx, board in enumerate(stats["STATS"]):
                    data.hashboards[idx].missing = True
                    chips = board.get("Num active chips")
                    if chips:
                        data.hashboards[idx].chips = chips
                        if chips > 0:
                            data.hashboards[idx].missing = False

        if all_data:
            if all_data.get("chain"):
                for idx, board in enumerate(all_data["chain"]):
                    temp = board.get("Temp min")
                    if temp:
                        data.hashboards[idx].temp = round(temp)

                    hashrate = board.get("Hash Rate H")
                    if hashrate:
                        data.hashboards[idx].hashrate = round(
                            hashrate / 1000000000000, 2
                        )

                    chip_temp = board.get("Temp max")
                    if chip_temp:
                        data.hashboards[idx].chip_temp = round(chip_temp)

            if all_data.get("fansSpeed"):
                speed = round((all_data["fansSpeed"] * 6000) / 100)
                for fan in range(self.fan_count):
                    setattr(data, f"fan_{fan+1}", speed)
            if all_data.get("mac"):
                data.mac = all_data["mac"].upper()
            else:
                mac = await self.get_mac()
                if mac:
                    data.mac = mac
            if all_data.get("power"):
                data.wattage = all_data["power"]

        if pools or all_data.get("pools_config"):
            pool_1 = None
            pool_2 = None
            pool_1_user = None
            pool_2_user = None
            pool_1_quota = 1
            pool_2_quota = 1
            quota = 0
            if pools:
                pools = pools[0]
                for pool in pools.get("POOLS"):
                    if not pool_1_user:
                        pool_1_user = pool.get("User")
                        pool_1 = pool["URL"]
                        if pool.get("Quota"):
                            pool_2_quota = pool.get("Quota")
                    elif not pool_2_user:
                        pool_2_user = pool.get("User")
                        pool_2 = pool["URL"]
                        if pool.get("Quota"):
                            pool_2_quota = pool.get("Quota")
                    if not pool.get("User") == pool_1_user:
                        if not pool_2_user == pool.get("User"):
                            pool_2_user = pool.get("User")
                            pool_2 = pool["URL"]
                            if pool.get("Quota"):
                                pool_2_quota = pool.get("Quota")
            elif all_data.get("pools_config"):
                print(all_data["pools_config"])
                for pool in all_data["pools_config"]:
                    if not pool_1_user:
                        pool_1_user = pool.get("user")
                        pool_1 = pool["url"]
                    elif not pool_2_user:
                        pool_2_user = pool.get("user")
                        pool_2 = pool["url"]
                    if not pool.get("user") == pool_1_user:
                        if not pool_2_user == pool.get("user"):
                            pool_2_user = pool.get("user")
                            pool_2 = pool["url"]

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

        return data
