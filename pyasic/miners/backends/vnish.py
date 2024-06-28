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

from typing import Optional

from pyasic import MinerConfig
from pyasic.data import AlgoHashRate, HashUnit
from pyasic.errors import APIError
from pyasic.miners.backends.bmminer import BMMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.firmware import VNishFirmware
from pyasic.web.vnish import VNishWebAPI

VNISH_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [WebAPICommand("web_settings", "settings")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_summary", "summary")],
        ),
    }
)


class VNish(VNishFirmware, BMMiner):
    """Handler for VNish miners"""

    _web_cls = VNishWebAPI
    web: VNishWebAPI

    supports_shutdown = True

    data_locations = VNISH_DATA_LOC

    async def restart_backend(self) -> bool:
        data = await self.web.restart_vnish()
        if data:
            try:
                return data["success"]
            except KeyError:
                pass
        return False

    async def stop_mining(self) -> bool:
        data = await self.web.stop_mining()
        if data:
            try:
                return data["success"]
            except KeyError:
                pass
        return False

    async def resume_mining(self) -> bool:
        data = await self.web.resume_mining()
        if data:
            try:
                return data["success"]
            except KeyError:
                pass
        return False

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            try:
                return data["success"]
            except KeyError:
                pass
        return False

    async def _get_mac(self, web_summary: dict = None) -> str:
        if web_summary is not None:
            try:
                mac = web_summary["system"]["network_status"]["mac"]
                return mac
            except KeyError:
                pass

        web_info = await self.web.info()

        if web_info is not None:
            try:
                mac = web_info["system"]["network_status"]["mac"]
                return mac
            except KeyError:
                pass

    async def fault_light_off(self) -> bool:
        result = await self.web.find_miner()
        if result is not None:
            if result.get("on") is False:
                return True
            else:
                await self.web.find_miner()

    async def fault_light_on(self) -> bool:
        result = await self.web.find_miner()
        if result is not None:
            if result.get("on") is True:
                return True
            else:
                await self.web.find_miner()

    async def _get_hostname(self, web_summary: dict = None) -> str:
        if web_summary is None:
            web_info = await self.web.info()

            if web_info is not None:
                try:
                    hostname = web_info["system"]["network_status"]["hostname"]
                    return hostname
                except KeyError:
                    pass

        if web_summary is not None:
            try:
                hostname = web_summary["system"]["network_status"]["hostname"]
                return hostname
            except KeyError:
                pass

    async def _get_wattage(self, web_summary: dict = None) -> Optional[int]:
        if web_summary is None:
            web_summary = await self.web.summary()

        if web_summary is not None:
            try:
                wattage = web_summary["miner"]["power_usage"]
                wattage = round(wattage)
                return wattage
            except KeyError:
                pass

    async def _get_hashrate(self, rpc_summary: dict = None) -> Optional[AlgoHashRate]:
        # get hr from API
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return AlgoHashRate.SHA256(
                    rpc_summary["SUMMARY"][0]["GHS 5s"], HashUnit.SHA256.GH
                ).into(self.algo.unit.default)
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_wattage_limit(self, web_settings: dict = None) -> Optional[int]:
        if web_settings is None:
            web_settings = await self.web.summary()

        if web_settings is not None:
            try:
                wattage_limit = web_settings["miner"]["overclock"]["preset"]
                if wattage_limit == "disabled":
                    return None
                return int(wattage_limit)
            except (KeyError, TypeError):
                pass

    async def _get_fw_ver(self, web_summary: dict = None) -> Optional[str]:
        if web_summary is None:
            web_summary = await self.web.summary()

        fw_ver = None
        if web_summary is not None:
            try:
                fw_ver = web_summary["miner"]["miner_type"]
                fw_ver = fw_ver.split("(Vnish ")[1].replace(")", "")
                return fw_ver
            except LookupError:
                return fw_ver

    async def _is_mining(self, web_summary: dict = None) -> Optional[bool]:
        if web_summary is None:
            web_summary = await self.web.summary()

        if web_summary is not None:
            try:
                is_mining = not web_summary["miner"]["miner_status"]["miner_state"] in [
                    "stopped",
                    "shutting-down",
                ]
                return is_mining
            except LookupError:
                pass

    async def get_config(self) -> MinerConfig:
        try:
            web_settings = await self.web.settings()
        except APIError:
            return self.config
        self.config = MinerConfig.from_vnish(web_settings)
        return self.config
