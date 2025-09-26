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
from typing import Any

from pyasic import APIError
from pyasic.data.boards import HashBoard
from pyasic.device.algorithm import AlgoHashRateType
from pyasic.miners.backends import AvalonMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.models import AvalonNano3, AvalonNano3s
from pyasic.web.avalonminer import AvalonMinerWebAPI

AVALON_NANO_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_minerinfo", "get_minerinfo")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_devs", "devs")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction(
            "_get_env_temp",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)

AVALON_NANO3S_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.ENVIRONMENT_TEMP): DataFunction(
            "_get_env_temp",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [RPCAPICommand("rpc_estats", "estats")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)


class CGMinerAvalonNano3(AvalonMiner, AvalonNano3):
    _web_cls = AvalonMinerWebAPI
    web: AvalonMinerWebAPI

    data_locations = AVALON_NANO_DATA_LOC

    async def _get_mac(self, web_minerinfo: dict[Any, Any] | None = None) -> str | None:
        if web_minerinfo is None:
            try:
                web_minerinfo = await self.web.minerinfo()
            except APIError:
                return None

        if web_minerinfo is not None:
            try:
                mac = web_minerinfo.get("mac")
                if mac is not None:
                    return mac.upper()
            except (KeyError, ValueError):
                pass
        return None


class CGMinerAvalonNano3s(AvalonMiner, AvalonNano3s):
    data_locations = AVALON_NANO3S_DATA_LOC

    async def _get_wattage(self, rpc_estats: dict | None = None) -> int | None:
        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                return None

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
                return int(parsed_estats["PS"][6])
            except (IndexError, KeyError, ValueError, TypeError):
                pass
        return None

    async def _get_hashrate(
        self, rpc_estats: dict | None = None
    ) -> AlgoHashRateType | None:
        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                return None

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
                return self.algo.hashrate(
                    rate=float(parsed_estats["GHSspd"]), unit=self.algo.unit.GH
                ).into(self.algo.unit.default)
            except (IndexError, KeyError, ValueError, TypeError):
                pass
        return None

    async def _get_hashboards(self, rpc_estats: dict | None = None) -> list[HashBoard]:
        hashboards = await AvalonMiner._get_hashboards(self, rpc_estats)

        if rpc_estats is None:
            try:
                rpc_estats = await self.rpc.estats()
            except APIError:
                return hashboards

        if rpc_estats is not None:
            try:
                parsed_estats = self.parse_estats(rpc_estats)["STATS"][0]["MM ID0"]
            except (IndexError, KeyError, ValueError, TypeError):
                return hashboards

            for board in range(len(hashboards)):
                try:
                    board_hr = parsed_estats["GHSspd"]
                    hashboards[board].hashrate = self.algo.hashrate(
                        rate=float(board_hr), unit=self.algo.unit.GH
                    ).into(self.algo.unit.default)
                except LookupError:
                    pass

        return hashboards
