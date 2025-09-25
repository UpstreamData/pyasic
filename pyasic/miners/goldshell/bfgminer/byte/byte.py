# ------------------------------------------------------------------------------
#  Copyright 2025 Upstream Data Inc                                            -
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

from pyasic.config import MinerConfig
from pyasic.data import Fan, MinerData
from pyasic.data.boards import HashBoard
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRateType, MinerAlgo
from pyasic.errors import APIError
from pyasic.miners.backends import GoldshellMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.models import Byte

ALGORITHM_SCRYPT_NAME = "scrypt(LTC)"
ALGORITHM_ZKSNARK_NAME = "zkSNARK(ALEO)"
EXPECTED_CHIPS_PER_SCRYPT_BOARD = 5
EXPECTED_CHIPS_PER_ZKSNARK_BOARD = 3

GOLDSHELL_BYTE_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_setting", "setting")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [WebAPICommand("web_setting", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_status", "status")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_devs", "devs")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_devs", "devs")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [
                RPCAPICommand("rpc_devs", "devs"),
                RPCAPICommand("rpc_devdetails", "devdetails"),
            ],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_devs", "devs")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_devs", "devs")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_devs", "devs")],
        ),
    }
)


class GoldshellByte(GoldshellMiner, Byte):
    data_locations = GOLDSHELL_BYTE_DATA_LOC
    supports_shutdown = False
    supports_power_modes = False
    web_devs: dict | None = None

    async def get_data(
        self,
        allow_warning: bool = False,
        include: list[str | DataOptions] | None = None,
        exclude: list[str | DataOptions] | None = None,
    ) -> MinerData:
        if self.web_devs is None:
            try:
                self.web_devs = await self.web.devs()
            except APIError:
                pass

        scrypt_board_count = 0
        zksnark_board_count = 0

        for minfo in (self.web_devs or {}).get("minfos", []):
            algo_name = minfo.get("name")

            for _ in minfo.get("infos", []):
                self.expected_hashboards += 1
                self.expected_fans += 1

                if algo_name == ALGORITHM_SCRYPT_NAME:
                    scrypt_board_count += 1
                elif algo_name == ALGORITHM_ZKSNARK_NAME:
                    zksnark_board_count += 1

        self.expected_chips = (EXPECTED_CHIPS_PER_SCRYPT_BOARD * scrypt_board_count) + (
            EXPECTED_CHIPS_PER_ZKSNARK_BOARD * zksnark_board_count
        )

        if scrypt_board_count > 0 and zksnark_board_count == 0:
            self.algo = MinerAlgo.SCRYPT  # type: ignore[assignment]
        elif zksnark_board_count > 0 and scrypt_board_count == 0:
            self.algo = MinerAlgo.ZKSNARK  # type: ignore[assignment]

        data = await super().get_data(allow_warning, include, exclude)
        data.expected_chips = self.expected_chips

        return data

    async def get_config(self) -> MinerConfig:
        try:
            pools = await self.web.pools()
        except APIError:
            return self.config or MinerConfig()

        self.config = MinerConfig.from_goldshell_byte(pools.get("groups", []))
        return self.config

    async def _get_api_ver(self, web_setting: dict | None = None) -> str | None:
        if web_setting is None:
            try:
                web_setting = await self.web.setting()
            except APIError:
                pass

        if web_setting is not None:
            try:
                version = web_setting.get("version")
                if version is not None:
                    self.api_ver = version.strip("v")
                    return self.api_ver
            except KeyError:
                pass

        return self.api_ver

    async def _get_expected_hashrate(
        self, rpc_devs: dict | None = None
    ) -> AlgoHashRateType | None:
        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        total_hash_rate_mh = 0.0

        if rpc_devs is not None:
            for board in rpc_devs.get("DEVS", []):
                algo_name = board.get("pool")

                if algo_name == ALGORITHM_SCRYPT_NAME:
                    total_hash_rate_mh += (
                        self.algo.hashrate(
                            rate=float(board.get("estimate_hash_rate", 0)),
                            unit=self.algo.unit.H,
                        )
                        .into(self.algo.unit.MH)
                        .rate
                    )
                elif algo_name == ALGORITHM_ZKSNARK_NAME:
                    total_hash_rate_mh += float(board.get("theory_hash", 0))

        hash_rate = self.algo.hashrate(
            rate=total_hash_rate_mh, unit=self.algo.unit.MH
        ).into(self.algo.unit.default)

        return hash_rate

    async def _get_hashrate(
        self, rpc_devs: dict | None = None
    ) -> AlgoHashRateType | None:
        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        total_hash_rate_mh = 0.0

        if rpc_devs is not None:
            for board in rpc_devs.get("DEVS", []):
                total_hash_rate_mh += float(board.get("MHS 20s", 0))

        hash_rate = self.algo.hashrate(
            rate=total_hash_rate_mh, unit=self.algo.unit.MH
        ).into(self.algo.unit.default)

        return hash_rate

    async def _get_pools(self, rpc_pools: dict | None = None) -> list[PoolMetrics]:
        if rpc_pools is None:
            try:
                rpc_pools = await self.rpc.pools()
            except APIError:
                pass

        pools_data = []
        if rpc_pools is not None:
            try:
                pools = rpc_pools.get("POOLS", [])
                for index, pool_info in enumerate(pools):
                    url = pool_info.get("URL")
                    pool_url = PoolUrl.from_str(url) if url else None
                    pool_data = PoolMetrics(
                        accepted=pool_info.get("Accepted"),
                        rejected=pool_info.get("Rejected"),
                        active=pool_info.get("Stratum Active"),
                        alive=pool_info.get("Status") == "Alive",
                        url=pool_url,
                        user=pool_info.get("User"),
                        index=index,
                    )
                    pools_data.append(pool_data)
            except LookupError:
                pass
        return pools_data

    async def _get_hashboards(
        self, rpc_devs: dict | None = None, rpc_devdetails: dict | None = None
    ) -> list[HashBoard]:
        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if rpc_devs is not None:
            for board in rpc_devs.get("DEVS", []):
                b_id = board["PGA"]
                hashboards[b_id].hashrate = self.algo.hashrate(
                    rate=float(board["MHS 20s"]), unit=self.algo.unit.MH
                ).into(self.algo.unit.default)
                hashboards[b_id].chip_temp = board["tstemp-1"]
                hashboards[b_id].temp = board["tstemp-2"]
                hashboards[b_id].voltage = board["voltage"]
                hashboards[b_id].active = board["Status"] == "Alive"
                hashboards[b_id].missing = False

                algo_name = board.get("pool")

                if algo_name == ALGORITHM_SCRYPT_NAME:
                    hashboards[b_id].expected_chips = EXPECTED_CHIPS_PER_SCRYPT_BOARD
                elif algo_name == ALGORITHM_ZKSNARK_NAME:
                    hashboards[b_id].expected_chips = EXPECTED_CHIPS_PER_ZKSNARK_BOARD

        if rpc_devdetails is None:
            try:
                rpc_devdetails = await self.rpc.devdetails()
            except APIError:
                pass

        if rpc_devdetails is not None:
            for board in rpc_devdetails.get("DEVS", []):
                b_id = board["DEVDETAILS"]
                hashboards[b_id].chips = board["chips-nr"]

        return hashboards

    async def _get_fans(self, rpc_devs: dict | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass

        fans_data = []

        if rpc_devs is not None:
            for board in rpc_devs.get("DEVS", []):
                if board.get("PGA") is not None:
                    try:
                        b_id = board["PGA"]
                        fan_speed = board[f"fan{b_id}"]
                        fans_data.append(fan_speed)

                    except KeyError:
                        pass

        fans = [Fan(speed=d) if d else Fan() for d in fans_data]

        return fans

    async def _get_uptime(self, web_devs: dict | None = None) -> int | None:
        if web_devs is None:
            try:
                web_devs = await self.web.devs()
            except APIError:
                pass

        if web_devs is not None:
            try:
                for minfo in (self.web_devs or {}).get("minfos", []):
                    for info in minfo.get("infos", []):
                        uptime = int(float(info["time"]))
                        return uptime
            except KeyError:
                pass

        return None

    async def _get_wattage(self, web_devs: dict | None = None) -> int | None:
        if web_devs is None:
            try:
                web_devs = await self.web.devs()
            except APIError:
                pass

        if web_devs is not None:
            try:
                for minfo in (self.web_devs or {}).get("minfos", []):
                    for info in minfo.get("infos", []):
                        wattage = int(float(info["power"]))
                        return wattage
            except KeyError:
                pass

        return None
