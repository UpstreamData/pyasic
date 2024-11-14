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

from pyasic import MinerConfig
from pyasic.data import AlgoHashRate, HashBoard, HashUnit
from pyasic.data.error_codes import MinerErrorData, X19Error
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.errors import APIError
from pyasic.miners.base import BaseMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.rpc.ccminer import CCMinerRPCAPI
from pyasic.web.hammer import HammerWebAPI

HAMMER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("web_get_blink_status", "get_blink_status")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_get_conf", "get_miner_conf")],
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


class BlackMiner(BaseMiner):
    """Handler for Hammer miners."""

    _rpc_cls = CCMinerRPCAPI
    rpc: CCMinerRPCAPI

    _web_cls = HammerWebAPI
    web: HammerWebAPI

    data_locations = HAMMER_DATA_LOC

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig.from_hammer(data)
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        await self.web.set_miner_conf(config.as_hammer(user_suffix=user_suffix))

    async def fault_light_on(self) -> bool:
        data = await self.web.blink(blink=True)
        if data:
            if data.get("code") == "B000":
                self.light = True
        return self.light

    async def fault_light_off(self) -> bool:
        data = await self.web.blink(blink=False)
        if data:
            if data.get("code") == "B100":
                self.light = False
        return self.light

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

    async def _get_hostname(self, web_get_system_info: dict = None) -> Optional[str]:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                return web_get_system_info["hostname"]
            except KeyError:
                pass

    async def _get_mac(self, web_get_system_info: dict = None) -> Optional[str]:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                return web_get_system_info["macaddr"]
            except KeyError:
                pass

        try:
            data = await self.web.get_network_info()
            if data:
                return data["macaddr"]
        except KeyError:
            pass

    async def _get_errors(self, web_summary: dict = None) -> List[MinerErrorData]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        errors = []
        if web_summary is not None:
            try:
                for item in web_summary["SUMMARY"][0]["status"]:
                    try:
                        if not item["status"] == "s":
                            errors.append(X19Error(item["msg"]))
                    except KeyError:
                        continue
            except LookupError:
                pass
        return errors

    async def _get_hashboards(self) -> List[HashBoard]:
        hashboards = [
            HashBoard(idx, expected_chips=self.expected_chips)
            for idx in range(self.expected_hashboards)
        ]

        try:
            rpc_stats = await self.web.stats(new_api=True)
        except APIError:
            return hashboards

        if rpc_stats is not None:
            try:
                for board in rpc_stats["STATS"][0]["chain"]:
                    hashboards[board["index"]].hashrate = AlgoHashRate.SHA256(
                        board["rate_real"], HashUnit.SHA256.GH
                    ).into(self.algo.unit.default)
                    hashboards[board["index"]].chips = board["asic_num"]
                    board_temp_data = list(
                        filter(lambda x: not x == 0, board["temp_pcb"])
                    )
                    hashboards[board["index"]].temp = sum(board_temp_data) / len(
                        board_temp_data
                    )
                    chip_temp_data = list(
                        filter(lambda x: not x == 0, board["temp_chip"])
                    )
                    hashboards[board["index"]].chip_temp = sum(chip_temp_data) / len(
                        chip_temp_data
                    )
                    hashboards[board["index"]].serial_number = board["sn"]
                    hashboards[board["index"]].missing = False
            except LookupError:
                pass
        return hashboards

    async def _get_fault_light(
        self, web_get_blink_status: dict = None
    ) -> Optional[bool]:
        if self.light:
            return self.light

        if web_get_blink_status is None:
            try:
                web_get_blink_status = await self.web.get_blink_status()
            except APIError:
                pass

        if web_get_blink_status is not None:
            try:
                self.light = web_get_blink_status["blink"]
            except KeyError:
                pass
        return self.light

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
        await self.web.set_network_conf(
            ip=ip,
            dns=dns,
            gateway=gateway,
            subnet_mask=subnet_mask,
            hostname=hostname,
            protocol=2,
        )

    async def set_dhcp(self, hostname: str = None):
        if not hostname:
            hostname = await self.get_hostname()
        await self.web.set_network_conf(
            ip="", dns="", gateway="", subnet_mask="", hostname=hostname, protocol=1
        )

    async def set_hostname(self, hostname: str):
        cfg = await self.web.get_network_info()
        dns = cfg["conf_dnsservers"]
        gateway = cfg["conf_gateway"]
        ip = cfg["conf_ipaddress"]
        subnet_mask = cfg["conf_netmask"]
        protocol = 1 if cfg["conf_nettype"] == "DHCP" else 2
        await self.web.set_network_conf(
            ip=ip,
            dns=dns,
            gateway=gateway,
            subnet_mask=subnet_mask,
            hostname=hostname,
            protocol=protocol,
        )

    async def _is_mining(self, web_get_conf: dict = None) -> Optional[bool]:
        if web_get_conf is None:
            try:
                web_get_conf = await self.web.get_miner_conf()
            except APIError:
                pass

        if web_get_conf is not None:
            try:
                if str(web_get_conf["bitmain-work-mode"]).isdigit():
                    return (
                        False if int(web_get_conf["bitmain-work-mode"]) == 1 else True
                    )
                return False
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
