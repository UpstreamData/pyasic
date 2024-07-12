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
from typing import List, Optional

from pyasic.config import MinerConfig
from pyasic.data import AlgoHashRate, Fan, HashBoard, HashUnit
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.errors import APIError
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, RPCAPICommand
from pyasic.miners.device.firmware import LuxOSFirmware
from pyasic.rpc.luxminer import LUXMinerRPCAPI

LUXMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [RPCAPICommand("rpc_config", "config")],
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
            [RPCAPICommand("rpc_power", "power")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_fans", "fans")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime", [RPCAPICommand("rpc_stats", "stats")]
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools", [RPCAPICommand("rpc_pools", "pools")]
        ),
    }
)


class LUXMiner(LuxOSFirmware):
    """Handler for LuxOS miners"""

    _rpc_cls = LUXMinerRPCAPI
    rpc: LUXMinerRPCAPI

    data_locations = LUXMINER_DATA_LOC

    async def _get_session(self) -> Optional[str]:
        try:
            data = await self.rpc.session()
            if not data["SESSION"][0]["SessionID"] == "":
                return data["SESSION"][0]["SessionID"]
        except APIError:
            pass

        try:
            data = await self.rpc.logon()
            return data["SESSION"][0]["SessionID"]
        except (LookupError, APIError):
            return

    async def fault_light_on(self) -> bool:
        try:
            session_id = await self._get_session()
            if session_id:
                await self.rpc.ledset(session_id, "red", "blink")
            return True
        except (APIError, LookupError):
            pass
        return False

    async def fault_light_off(self) -> bool:
        try:
            session_id = await self._get_session()
            if session_id:
                await self.rpc.ledset(session_id, "red", "off")
            return True
        except (APIError, LookupError):
            pass
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_luxminer()

    async def restart_luxminer(self) -> bool:
        try:
            session_id = await self._get_session()
            if session_id:
                await self.rpc.resetminer(session_id)
            return True
        except (APIError, LookupError):
            pass
        return False

    async def stop_mining(self) -> bool:
        try:
            session_id = await self._get_session()
            if session_id:
                await self.rpc.curtail(session_id)
            return True
        except (APIError, LookupError):
            pass
        return False

    async def resume_mining(self) -> bool:
        try:
            session_id = await self._get_session()
            if session_id:
                await self.rpc.wakeup(session_id)
            return True
        except (APIError, LookupError):
            pass

    async def reboot(self) -> bool:
        try:
            session_id = await self._get_session()
            if session_id:
                await self.rpc.rebootdevice(session_id)
            return True
        except (APIError, LookupError):
            pass
        return False

    async def get_config(self) -> MinerConfig:
        return self.config

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(self, rpc_config: dict = None) -> Optional[str]:
        mac = None
        if rpc_config is None:
            try:
                rpc_config = await self.rpc.config()
            except APIError:
                return None

        if rpc_config is not None:
            try:
                mac = rpc_config["CONFIG"][0]["MACAddr"]
            except KeyError:
                return None

        return mac

    async def _get_hashrate(self, rpc_summary: dict = None) -> Optional[AlgoHashRate]:
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

    async def _get_hashboards(self, rpc_stats: dict = None) -> List[HashBoard]:
        hashboards = []

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                board_offset = -1
                boards = rpc_stats["STATS"]
                if len(boards) > 1:
                    for board_num in range(1, 16, 5):
                        for _b_num in range(5):
                            b = boards[1].get(f"chain_acn{board_num + _b_num}")

                            if b and not b == 0 and board_offset == -1:
                                board_offset = board_num
                    if board_offset == -1:
                        board_offset = 1

                    for i in range(
                        board_offset, board_offset + self.expected_hashboards
                    ):
                        hashboard = HashBoard(
                            slot=i - board_offset, expected_chips=self.expected_chips
                        )

                        chip_temp = boards[1].get(f"temp{i}")
                        if chip_temp:
                            hashboard.chip_temp = round(chip_temp)

                        temp = boards[1].get(f"temp2_{i}")
                        if temp:
                            hashboard.temp = round(temp)

                        hashrate = boards[1].get(f"chain_rate{i}")
                        if hashrate:
                            hashboard.hashrate = AlgoHashRate.SHA256(
                                hashrate, HashUnit.SHA256.GH
                            ).into(self.algo.unit.default)

                        chips = boards[1].get(f"chain_acn{i}")
                        if chips:
                            hashboard.chips = chips
                            hashboard.missing = False
                        if (not chips) or (not chips > 0):
                            hashboard.missing = True
                        hashboards.append(hashboard)
            except (LookupError, ValueError, TypeError):
                pass

        return hashboards

    async def _get_wattage(self, rpc_power: dict = None) -> Optional[int]:
        if rpc_power is None:
            try:
                rpc_power = await self.rpc.power()
            except APIError:
                pass

        if rpc_power is not None:
            try:
                return rpc_power["POWER"][0]["Watts"]
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_fans(self, rpc_fans: dict = None) -> List[Fan]:
        if rpc_fans is None:
            try:
                rpc_fans = await self.rpc.fans()
            except APIError:
                pass

        fans = []

        if rpc_fans is not None:
            for fan in range(self.expected_fans):
                try:
                    fans.append(Fan(rpc_fans["FANS"][fan]["RPM"]))
                except (LookupError, ValueError, TypeError):
                    fans.append(Fan())
        return fans

    async def _get_expected_hashrate(
        self, rpc_stats: dict = None
    ) -> Optional[AlgoHashRate]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                expected_rate = rpc_stats["STATS"][1]["total_rateideal"]
                try:
                    rate_unit = rpc_stats["STATS"][1]["rate_unit"]
                except KeyError:
                    rate_unit = "GH"
                return AlgoHashRate.SHA256(
                    expected_rate, HashUnit.SHA256.from_str(rate_unit)
                ).into(self.algo.unit.default)
            except LookupError:
                pass

    async def _get_uptime(self, rpc_stats: dict = None) -> Optional[int]:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                return int(rpc_stats["STATS"][1]["Elapsed"])
            except LookupError:
                pass

    async def _get_pools(self, rpc_pools: dict = None) -> List[PoolMetrics]:
        if rpc_pools is None:
            try:
                rpc_pools = await self.rpc.pools()
            except APIError:
                pass

        pools_data = []
        if rpc_pools is not None:
            try:
                pools = rpc_pools.get("POOLS", [])
                for pool_info in pools:
                    url = pool_info.get("URL")
                    pool_url = PoolUrl.from_str(url) if url else None
                    pool_data = PoolMetrics(
                        accepted=pool_info.get("Accepted"),
                        rejected=pool_info.get("Rejected"),
                        get_failures=pool_info.get("Get Failures"),
                        remote_failures=pool_info.get("Remote Failures"),
                        active=pool_info.get("Stratum Active"),
                        alive=pool_info.get("Status") == "Alive",
                        url=pool_url,
                        user=pool_info.get("User"),
                        index=pool_info.get("POOL"),
                    )
                    pools_data.append(pool_data)
            except LookupError:
                pass
        return pools_data
