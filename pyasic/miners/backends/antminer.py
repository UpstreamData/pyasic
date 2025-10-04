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

import logging
from pathlib import Path
from typing import Any

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModeConfig
from pyasic.data.boards import HashBoard
from pyasic.data.error_codes.X19 import X19Error
from pyasic.data.fans import Fan
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.miners.backends.bmminer import BMMiner
from pyasic.miners.backends.cgminer import CGMiner
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.rpc.antminer import AntminerRPCAPI
from pyasic.ssh.antminer import AntminerModernSSH
from pyasic.web.antminer import AntminerModernWebAPI, AntminerOldWebAPI

ANTMINER_MODERN_DATA_LOC = DataLocations(
    **{
        str(DataOptions.SERIAL_NUMBER): DataFunction(
            "_get_serial_number",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
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
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [],
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


class AntminerModern(BMMiner):
    """Handler for AntMiners with the modern web interface, such as S19"""

    _web_cls = AntminerModernWebAPI
    web: AntminerModernWebAPI

    _rpc_cls = AntminerRPCAPI
    rpc: AntminerRPCAPI

    _ssh_cls = AntminerModernSSH
    ssh: AntminerModernSSH

    data_locations = ANTMINER_MODERN_DATA_LOC

    supports_shutdown = True
    supports_power_modes = True

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig.from_am_modern(data)
        return self.config or MinerConfig()

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        self.config = config
        await self.web.set_miner_conf(config.as_am_modern(user_suffix=user_suffix))
        # if data:
        #     if data.get("code") == "M000":
        #         return
        #
        # for i in range(7):
        #     data = await self.get_config()
        #     if data == self.config:
        #         break
        #     await asyncio.sleep(1)

    async def upgrade_firmware(
        self,
        *,
        file: str | None = None,
        url: str | None = None,
        version: str | None = None,
        keep_settings: bool = True,
    ) -> bool:
        """
        Upgrade the firmware of the AntMiner device.

        Args:
            file: Path to the firmware file as a string.
            url: URL to download firmware from (not implemented).
            version: Version to upgrade to (not implemented).
            keep_settings: Whether to keep the current settings after the update.

        Returns:
            bool: True if upgrade was successful, False otherwise.
        """
        if not file:
            logging.error("File location must be provided for firmware upgrade.")
            return False

        if url or version:
            logging.warning(
                "URL and version parameters are not implemented for Antminer."
            )

        try:
            file_path = Path(file)

            if not hasattr(self.web, "update_firmware"):
                logging.error(
                    "Firmware upgrade not supported via web API for this Antminer model."
                )
                return False

            result = await self.web.update_firmware(
                file=file_path, keep_settings=keep_settings
            )

            if result.get("success"):
                logging.info(
                    "Firmware upgrade process completed successfully for AntMiner."
                )
                return True
            else:
                error_message = result.get("message", "Unknown error")
                logging.error(f"Firmware upgrade failed. Response: {error_message}")
                return False
        except Exception as e:
            logging.error(
                f"An error occurred during the firmware upgrade process: {e}",
                exc_info=True,
            )
            return False

    async def fault_light_on(self) -> bool:
        data = await self.web.blink(blink=True)
        if data:
            if data.get("code") == "B000":
                self.light = True
        return self.light or False

    async def fault_light_off(self) -> bool:
        data = await self.web.blink(blink=False)
        if data:
            if data.get("code") == "B100":
                self.light = False
        return self.light or False

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

    async def stop_mining(self) -> bool:
        cfg = await self.get_config()
        cfg.mining_mode = MiningModeConfig.sleep()
        await self.send_config(cfg)
        return True

    async def resume_mining(self) -> bool:
        cfg = await self.get_config()
        cfg.mining_mode = MiningModeConfig.normal()
        await self.send_config(cfg)
        return True

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
                return str(web_get_system_info["hostname"])
            except KeyError:
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
                return str(web_get_system_info["macaddr"])
            except KeyError:
                pass

        try:
            data = await self.web.get_network_info()
            if data:
                return str(data["macaddr"])
        except KeyError:
            pass
        return None

    async def _get_errors(  # type: ignore[override]
        self, web_summary: dict[str, Any] | None = None
    ) -> list[X19Error]:
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
                            errors.append(X19Error(error_message=item["msg"]))
                    except KeyError:
                        continue
            except LookupError:
                pass
        return errors

    async def _get_hashboards(self) -> list[HashBoard]:  # type: ignore[override]
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=idx, expected_chips=self.expected_chips)
            for idx in range(self.expected_hashboards)
        ]

        try:
            rpc_stats = await self.rpc.stats(new_api=True)
        except APIError:
            return hashboards

        if rpc_stats is not None:
            try:
                for board in rpc_stats["STATS"][0]["chain"]:
                    hashboards[board["index"]].hashrate = self.algo.hashrate(
                        rate=board["rate_real"],
                        unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    )
                    hashboards[board["index"]].chips = board["asic_num"]

                    if "S21+ Hyd" in self.model:
                        hashboards[board["index"]].inlet_temp = board["temp_pcb"][0]
                        hashboards[board["index"]].outlet_temp = board["temp_pcb"][2]
                        hashboards[board["index"]].chip_temp = board["temp_pic"][0]
                        board_temp_data = list(
                            filter(
                                lambda x: not x == 0,
                                [
                                    board["temp_pic"][1],
                                    board["temp_pic"][2],
                                    board["temp_pic"][3],
                                    board["temp_pcb"][1],
                                    board["temp_pcb"][3],
                                ],
                            )
                        )
                        hashboards[board["index"]].temp = (
                            sum(board_temp_data) / len(board_temp_data)
                            if len(board_temp_data) > 0
                            else 0
                        )

                    else:
                        board_temp_data = list(
                            filter(lambda x: not x == 0, board["temp_pcb"])
                        )
                        hashboards[board["index"]].temp = (
                            sum(board_temp_data) / len(board_temp_data)
                            if len(board_temp_data) > 0
                            else 0
                        )
                        chip_temp_data = list(
                            filter(lambda x: not x == 0, board["temp_chip"])
                        )
                        hashboards[board["index"]].chip_temp = (
                            sum(chip_temp_data) / len(chip_temp_data)
                            if len(chip_temp_data) > 0
                            else 0
                        )

                    hashboards[board["index"]].serial_number = board["sn"]
                    hashboards[board["index"]].missing = False
            except LookupError:
                pass
        return hashboards

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
                self.light = web_get_blink_status["blink"]
            except KeyError:
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
                expected_rate = rpc_stats["STATS"][1]["total_rateideal"]
                try:
                    rate_unit = rpc_stats["STATS"][1]["rate_unit"]
                except KeyError:
                    rate_unit = "GH"
                return self.algo.hashrate(
                    rate=float(expected_rate), unit=self.algo.unit.from_str(rate_unit)
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except LookupError:
                pass
        return None

    async def _get_serial_number(
        self, web_get_system_info: dict[str, Any] | None = None
    ) -> str | None:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                return str(web_get_system_info["serinum"])
            except LookupError:
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
                if str(web_get_conf["bitmain-work-mode"]).isdigit():
                    return (
                        False if int(web_get_conf["bitmain-work-mode"]) == 1 else True
                    )
                return False
            except LookupError:
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
                return int(rpc_stats["STATS"][1]["Elapsed"])
            except LookupError:
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


ANTMINER_OLD_DATA_LOC = DataLocations(
    **{
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
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [RPCAPICommand("rpc_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_stats", "stats")],
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


class AntminerOld(CGMiner):
    """Handler for AntMiners with the old web interface, such as S17"""

    _web_cls = AntminerOldWebAPI
    web: AntminerOldWebAPI

    data_locations = ANTMINER_OLD_DATA_LOC

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig.from_am_old(data)
        return self.config or MinerConfig()

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        self.config = config
        await self.web.set_miner_conf(config.as_am_old(user_suffix=user_suffix))

    async def _get_mac(self) -> str | None:
        try:
            data = await self.web.get_system_info()
            if data:
                return str(data["macaddr"])
        except KeyError:
            pass
        return None

    async def fault_light_on(self) -> bool:
        # this should time out, after it does do a check
        await self.web.blink(blink=True)
        try:
            data = await self.web.get_blink_status()
            if data:
                if data["isBlinking"]:
                    self.light = True
        except KeyError:
            pass
        return self.light or False

    async def fault_light_off(self) -> bool:
        await self.web.blink(blink=False)
        try:
            data = await self.web.get_blink_status()
            if data:
                if not data["isBlinking"]:
                    self.light = False
        except KeyError:
            pass
        return self.light or False

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

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
                self.light = web_get_blink_status["isBlinking"]
            except KeyError:
                pass
        return self.light

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
                return str(web_get_system_info["hostname"])
            except KeyError:
                pass
        return None

    async def _get_fans(self, rpc_stats: dict[str, Any] | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass

        fans_data = [Fan() for _ in range(self.expected_fans)]
        if rpc_stats is not None:
            try:
                fan_offset = -1

                for fan_num in range(1, 8, 4):
                    for _f_num in range(4):
                        f = rpc_stats["STATS"][1].get(f"fan{fan_num + _f_num}")
                        if f and not f == 0 and fan_offset == -1:
                            fan_offset = fan_num + 2
                if fan_offset == -1:
                    fan_offset = 3

                for fan in range(self.expected_fans):
                    fans_data[fan].speed = rpc_stats["STATS"][1].get(
                        f"fan{fan_offset + fan}", 0
                    )
            except LookupError:
                pass
        return fans_data

    async def _get_hashboards(
        self, rpc_stats: dict[str, Any] | None = None
    ) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []
        hashboards: list[HashBoard] = []

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
                            hashboard.hashrate = self.algo.hashrate(
                                rate=float(hashrate),
                                unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                            ).into(
                                self.algo.unit.default  # type: ignore[attr-defined]
                            )

                        chips = boards[1].get(f"chain_acn{i}")
                        if chips:
                            hashboard.chips = chips
                            hashboard.missing = False
                        if (not chips) or (not chips > 0):
                            hashboard.missing = True
                        hashboards.append(hashboard)
            except LookupError:
                return [
                    HashBoard(slot=i, expected_chips=self.expected_chips)
                    for i in range(self.expected_hashboards)
                ]

        return hashboards

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
                return False if int(web_get_conf["bitmain-work-mode"]) == 1 else True
            except LookupError:
                pass

        rpc_summary = None
        try:
            rpc_summary = await self.rpc.summary()
        except APIError:
            pass

        if rpc_summary is not None:
            if not rpc_summary == {}:
                return True
            else:
                return False

        return None

    async def _get_uptime(self, rpc_stats: dict[str, Any] | None = None) -> int | None:
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
        return None
