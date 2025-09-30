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

from pydantic import BaseModel, Field, ValidationError

from pyasic.config import MinerConfig
from pyasic.data.boards import HashBoard
from pyasic.data.error_codes import MinerErrorData
from pyasic.data.error_codes.X19 import X19Error
from pyasic.data.fans import Fan
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.firmware import StockFirmware
from pyasic.rpc.ccminer import CCMinerRPCAPI
from pyasic.web.hammer import HammerWebAPI


class HammerSystemInfo(BaseModel):
    hostname: str
    macaddr: str

    class Config:
        extra = "allow"


class HammerNetworkInfo(BaseModel):
    macaddr: str
    conf_dnsservers: str
    conf_gateway: str
    conf_ipaddress: str
    conf_netmask: str
    conf_nettype: str

    class Config:
        extra = "allow"


class HammerBlinkStatus(BaseModel):
    blink: bool

    class Config:
        extra = "allow"


class HammerBlinkResponse(BaseModel):
    code: str

    class Config:
        extra = "allow"


class HammerMinerConf(BaseModel):
    bitmain_work_mode: str | int = Field(alias="bitmain-work-mode")

    class Config:
        extra = "allow"
        populate_by_name = True


class HammerVersionInfo(BaseModel):
    API: str
    CompileTime: str

    class Config:
        extra = "allow"


class HammerVersionWrapper(BaseModel):
    VERSION: list[HammerVersionInfo]

    class Config:
        extra = "allow"


class HammerSummaryInfo(BaseModel):
    MHS_5s: float = Field(alias="MHS 5s")

    class Config:
        extra = "allow"
        populate_by_name = True


class HammerSummaryWrapper(BaseModel):
    SUMMARY: list[HammerSummaryInfo]

    class Config:
        extra = "allow"


class HammerStatsInfo(BaseModel):
    Elapsed: int
    total_rateideal: float | None = None
    rate_unit: str = "MH"

    class Config:
        extra = "allow"


class HammerStatsWrapper(BaseModel):
    STATS: list[Any]  # Mixed list with different structures

    class Config:
        extra = "allow"


class HammerPoolInfo(BaseModel):
    URL: str | None = None
    User: str | None = None
    Status: str = ""
    Stratum_Active: bool = Field(False, alias="Stratum Active")
    Accepted: int = 0
    Rejected: int = 0
    Get_Failures: int = Field(0, alias="Get Failures")
    Remote_Failures: int = Field(0, alias="Remote Failures")
    POOL: int = 0

    class Config:
        extra = "allow"
        populate_by_name = True


class HammerPoolsWrapper(BaseModel):
    POOLS: list[HammerPoolInfo]

    class Config:
        extra = "allow"


class HammerStatusItem(BaseModel):
    status: str
    msg: str

    class Config:
        extra = "allow"


class HammerWebSummaryInfo(BaseModel):
    status: list[HammerStatusItem]

    class Config:
        extra = "allow"


class HammerWebSummaryWrapper(BaseModel):
    SUMMARY: list[HammerWebSummaryInfo]

    class Config:
        extra = "allow"


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
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_stats", "stats")],
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


class BlackMiner(StockFirmware):
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
        return self.config or MinerConfig()

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        self.config = config
        await self.web.set_miner_conf(config.as_hammer(user_suffix=user_suffix))

    async def fault_light_on(self) -> bool:
        data = await self.web.blink(blink=True)
        if data:
            try:
                response = HammerBlinkResponse.model_validate(data)
                if response.code == "B000":
                    self.light = True
            except ValidationError:
                pass
        return self.light or False

    async def fault_light_off(self) -> bool:
        data = await self.web.blink(blink=False)
        if data:
            try:
                response = HammerBlinkResponse.model_validate(data)
                if response.code == "B100":
                    self.light = False
            except ValidationError:
                pass
        return self.light or False

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

    async def _get_api_ver(
        self, rpc_version: dict[str, Any] | None = None
    ) -> str | None:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                version_response = HammerVersionWrapper.model_validate(rpc_version)
                self.api_ver = version_response.VERSION[0].API
            except ValidationError:
                pass

        return self.api_ver

    async def _get_fw_ver(
        self, rpc_version: dict[str, Any] | None = None
    ) -> str | None:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                version_response = HammerVersionWrapper.model_validate(rpc_version)
                self.fw_ver = version_response.VERSION[0].CompileTime
            except ValidationError:
                pass

        return self.fw_ver

    async def _get_hashrate(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        # get hr from API
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                summary_response = HammerSummaryWrapper.model_validate(rpc_summary)
                return self.algo.hashrate(
                    rate=summary_response.SUMMARY[0].MHS_5s,
                    unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError:
                pass
        return None

    async def _get_hashboards(
        self, rpc_stats: dict[str, Any] | None = None
    ) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = []

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                stats_wrapper = HammerStatsWrapper.model_validate(rpc_stats)
                boards = stats_wrapper.STATS
                if len(boards) > 1:
                    board_data = boards[1]
                    board_offset = -1
                    for board_num in range(1, 16, 5):
                        for _b_num in range(5):
                            b = board_data.get(f"chain_acn{board_num + _b_num}")

                            if b and not b == 0 and board_offset == -1:
                                board_offset = board_num
                    if board_offset == -1:
                        board_offset = 1

                    real_slots = []

                    for i in range(board_offset, board_offset + 4):
                        key = f"chain_acs{i}"
                        if board_data.get(key, "") != "":
                            real_slots.append(i)

                    if len(real_slots) < 3:
                        real_slots = list(
                            range(board_offset, board_offset + self.expected_hashboards)
                        )

                    for i in real_slots:
                        hashboard = HashBoard(
                            slot=i - board_offset, expected_chips=self.expected_chips
                        )
                        temp = board_data.get(f"temp{i}")
                        if temp:
                            hashboard.chip_temp = round(temp)
                            hashboard.temp = round(temp)

                        hashrate = board_data.get(f"chain_rate{i}")
                        if hashrate:
                            hashboard.hashrate = self.algo.hashrate(
                                rate=float(hashrate),
                                unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                            ).into(
                                self.algo.unit.default  # type: ignore[attr-defined]
                            )

                        chips = board_data.get(f"chain_acn{i}")
                        if chips:
                            hashboard.chips = chips
                            hashboard.missing = False
                        if (not chips) or (not chips > 0):
                            hashboard.missing = True
                        hashboards.append(hashboard)
            except (ValidationError, ValueError, TypeError):
                pass

        return hashboards

    async def _get_fans(self, rpc_stats: dict[str, Any] | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        fans = [Fan() for _ in range(self.expected_fans)]
        if rpc_stats is not None:
            try:
                stats_wrapper = HammerStatsWrapper.model_validate(rpc_stats)
                if len(stats_wrapper.STATS) > 1:
                    fan_data = stats_wrapper.STATS[1]
                    fan_offset = -1

                    for fan_num in range(1, 8, 4):
                        for _f_num in range(4):
                            f = fan_data.get(f"fan{fan_num + _f_num}", 0)
                            if f and not f == 0 and fan_offset == -1:
                                fan_offset = fan_num
                    if fan_offset == -1:
                        fan_offset = 1

                    for fan in range(self.expected_fans):
                        fans[fan].speed = fan_data.get(f"fan{fan_offset + fan}", 0)
            except ValidationError:
                pass

        return fans

    async def _get_hostname(
        self, web_get_system_info: dict[str, Any] | None = None
    ) -> str | None:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                system_info = HammerSystemInfo.model_validate(web_get_system_info)
                return system_info.hostname
            except ValidationError:
                pass
        return None

    async def _get_mac(
        self, web_get_system_info: dict[str, Any] | None = None
    ) -> str | None:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                system_info = HammerSystemInfo.model_validate(web_get_system_info)
                return system_info.macaddr
            except ValidationError:
                pass

        try:
            data = await self.web.get_network_info()
            if data:
                network_info = HammerNetworkInfo.model_validate(data)
                return network_info.macaddr
        except (APIError, ValidationError):
            pass
        return None

    async def _get_errors(
        self, web_summary: dict[str, Any] | None = None
    ) -> list[MinerErrorData]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        errors = []
        if web_summary is not None:
            try:
                summary_response = HammerWebSummaryWrapper.model_validate(web_summary)
                for item in summary_response.SUMMARY[0].status:
                    if item.status != "s":
                        errors.append(X19Error(error_message=item.msg))
            except ValidationError:
                pass
        return errors  # type: ignore[return-value]

    async def _get_fault_light(
        self, web_get_blink_status: dict[str, Any] | None = None
    ) -> bool | None:
        if self.light:
            return self.light

        if web_get_blink_status is None:
            try:
                web_get_blink_status = await self.web.get_blink_status()
            except APIError:
                pass

        if web_get_blink_status is not None:
            try:
                blink_status = HammerBlinkStatus.model_validate(web_get_blink_status)
                self.light = blink_status.blink
            except ValidationError:
                pass
        return self.light

    async def _get_expected_hashrate(
        self, rpc_stats: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                stats_wrapper = HammerStatsWrapper.model_validate(rpc_stats)
                if len(stats_wrapper.STATS) > 1:
                    stats_info = HammerStatsInfo.model_validate(stats_wrapper.STATS[1])
                    expected_rate = stats_info.total_rateideal
                    if expected_rate is None:
                        if (
                            hasattr(self, "sticker_hashrate")
                            and self.sticker_hashrate is not None
                        ):
                            result = self.sticker_hashrate.into(self.algo.unit.default)  # type: ignore[attr-defined]
                            return result  # type: ignore[no-any-return]
                        return None
                    return self.algo.hashrate(
                        rate=expected_rate,
                        unit=self.algo.unit.from_str(stats_info.rate_unit),
                    ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError:
                pass
        return None

    async def set_static_ip(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str = "255.255.255.0",
        hostname: str | None = None,
    ) -> None:
        if not hostname:
            hostname = await self.get_hostname() or ""
        await self.web.set_network_conf(
            ip=ip,
            dns=dns,
            gateway=gateway,
            subnet_mask=subnet_mask,
            hostname=hostname,
            protocol=2,
        )

    async def set_dhcp(self, hostname: str | None = None) -> None:
        if not hostname:
            hostname = await self.get_hostname() or ""
        await self.web.set_network_conf(
            ip="", dns="", gateway="", subnet_mask="", hostname=hostname, protocol=1
        )

    async def set_hostname(self, hostname: str) -> None:
        cfg = await self.web.get_network_info()
        network_info = HammerNetworkInfo.model_validate(cfg)
        dns = network_info.conf_dnsservers
        gateway = network_info.conf_gateway
        ip = network_info.conf_ipaddress
        subnet_mask = network_info.conf_netmask
        protocol = 1 if network_info.conf_nettype == "DHCP" else 2
        await self.web.set_network_conf(
            ip=ip,
            dns=dns,
            gateway=gateway,
            subnet_mask=subnet_mask,
            hostname=hostname,
            protocol=protocol,
        )

    async def _is_mining(
        self, web_get_conf: dict[str, Any] | None = None
    ) -> bool | None:
        if web_get_conf is None:
            try:
                web_get_conf = await self.web.get_miner_conf()
            except APIError:
                pass

        if web_get_conf is not None:
            try:
                miner_conf = HammerMinerConf.model_validate(web_get_conf)
                work_mode = str(miner_conf.bitmain_work_mode)
                if work_mode.isdigit():
                    return int(work_mode) != 1
                return False
            except ValidationError:
                pass
        return None

    async def _get_uptime(self, rpc_stats: dict[str, Any] | None = None) -> int | None:
        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        if rpc_stats is not None:
            try:
                stats_wrapper = HammerStatsWrapper.model_validate(rpc_stats)
                if len(stats_wrapper.STATS) > 1:
                    stats_info = HammerStatsInfo.model_validate(stats_wrapper.STATS[1])
                    return stats_info.Elapsed
            except ValidationError:
                pass
        return None

    async def _get_pools(
        self, rpc_pools: dict[str, Any] | None = None
    ) -> list[PoolMetrics]:
        if rpc_pools is None:
            try:
                rpc_pools = await self.rpc.pools()
            except APIError:
                pass

        pools_data = []
        if rpc_pools is not None:
            try:
                pools_response = HammerPoolsWrapper.model_validate(rpc_pools)
                for pool_info in pools_response.POOLS:
                    pool_url = (
                        PoolUrl.from_str(pool_info.URL) if pool_info.URL else None
                    )
                    pool_data = PoolMetrics(
                        accepted=pool_info.Accepted,
                        rejected=pool_info.Rejected,
                        get_failures=pool_info.Get_Failures,
                        remote_failures=pool_info.Remote_Failures,
                        active=pool_info.Stratum_Active,
                        alive=pool_info.Status == "Alive",
                        url=pool_url,
                        user=pool_info.User,
                        index=pool_info.POOL,
                    )
                    pools_data.append(pool_data)
            except ValidationError:
                pass
        return pools_data
