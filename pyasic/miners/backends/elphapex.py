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

from pyasic import APIError, MinerConfig
from pyasic.data import Fan, HashBoard, X19Error
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRateType
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    WebAPICommand,
)
from pyasic.miners.device.firmware import StockFirmware
from pyasic.web.elphapex import ElphapexWebAPI

ELPHAPEX_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_get_system_info", "get_system_info")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("web_stats", "stats")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [WebAPICommand("web_stats", "stats")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_stats", "stats")],
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
            [WebAPICommand("web_get_miner_conf", "get_miner_conf")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [WebAPICommand("web_pools", "pools")],
        ),
    }
)


class ElphapexMiner(StockFirmware):
    """Handler for Elphapex miners."""

    _web_cls = ElphapexWebAPI
    web: ElphapexWebAPI

    data_locations = ELPHAPEX_DATA_LOC

    async def get_config(self) -> MinerConfig:
        data = await self.web.get_miner_conf()
        if data:
            self.config = MinerConfig.from_elphapex(data)
        if self.config is None:
            self.config = MinerConfig()
        return self.config

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        self.config = config
        await self.web.set_miner_conf(config.as_elphapex(user_suffix=user_suffix))

    async def fault_light_on(self) -> bool:
        data = await self.web.blink(blink=True)
        if data:
            if data.get("code") == "B000":
                self.light = True
        return self.light if self.light is not None else False

    async def fault_light_off(self) -> bool:
        data = await self.web.blink(blink=False)
        if data:
            if data.get("code") == "B100":
                self.light = False
        return self.light if self.light is not None else False

    async def reboot(self) -> bool:
        data = await self.web.reboot()
        if data:
            return True
        return False

    async def _get_api_ver(self, web_summary: dict | None = None) -> str | None:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                self.api_ver = web_summary["STATUS"]["api_version"]
            except LookupError:
                pass

        return self.api_ver

    async def _get_fw_ver(self, web_get_system_info: dict | None = None) -> str | None:
        if web_get_system_info is None:
            try:
                web_get_system_info = await self.web.get_system_info()
            except APIError:
                pass

        if web_get_system_info is not None:
            try:
                self.fw_ver = (
                    web_get_system_info["system_filesystem_version"]
                    .upper()
                    .split("V")[-1]
                )
            except LookupError:
                pass

        return self.fw_ver

    async def _get_hostname(
        self, web_get_system_info: dict | None = None
    ) -> str | None:
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
        return None

    async def _get_mac(self, web_get_system_info: dict | None = None) -> str | None:
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
        return None

    async def _get_errors(  # type: ignore[override]
        self, web_summary: dict | None = None
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

    async def _get_hashboards(self, web_stats: dict | None = None) -> list[HashBoard]:
        """Build the list of ``HashBoard`` records from ``stats.cgi``."""
        # Tolerates partially-supported devices (model resolved but
        # ``expected_hashboards`` is ``None``), missing/malformed payloads,
        # and sparsely-populated chains (e.g. DG-Home1 ships with 1 of 4
        # chains populated). See ``_resolve_expected_hashboards`` for the
        # slot-count fallback rationale.
        if web_stats is None:
            try:
                web_stats = await self.web.stats()
            except APIError:
                web_stats = None

        expected = self._resolve_expected_hashboards(web_stats)
        if expected is None:
            return []

        hashboards = [
            HashBoard(slot=idx, expected_chips=self.expected_chips)
            for idx in range(expected)
        ]
        for board in self._iter_stats_chains(web_stats):
            self._apply_chain_to_board(hashboards, board)
        return hashboards

    def _resolve_expected_hashboards(self, web_stats: dict | None) -> int | None:
        """Return the number of hashboard slots to model."""
        # Falls back to ``STATS[0].chain_num`` (or ``len(STATS[0].chain)``)
        # when the device is only partially supported and
        # ``self.expected_hashboards`` is ``None``. Without this,
        # ``range(self.expected_hashboards)`` raises ``TypeError`` and bubbles
        # up as ``APIError`` for DG-Home1 on pyasic 0.79.0
        # (see UpstreamData/pyasic#311, #428).
        if self.expected_hashboards is not None:
            return self.expected_hashboards
        if not isinstance(web_stats, dict):
            return None
        try:
            stats0 = web_stats["STATS"][0]
        except (LookupError, TypeError):
            return None
        chain_num = stats0.get("chain_num")
        if chain_num is None and isinstance(stats0.get("chain"), list):
            chain_num = len(stats0["chain"])
        if isinstance(chain_num, int) and chain_num > 0:
            return chain_num
        return None

    @staticmethod
    def _iter_stats_chains(web_stats: dict | None) -> list[dict]:
        """Return the per-chain stats list, or an empty list if missing."""
        if not isinstance(web_stats, dict):
            return []
        try:
            chains = web_stats["STATS"][0]["chain"]
        except (LookupError, TypeError):
            return []
        return chains if isinstance(chains, list) else []

    def _apply_chain_to_board(self, hashboards: list[HashBoard], board: dict) -> None:
        """Populate a single ``HashBoard`` from a ``stats.cgi`` chain entry."""
        board_index = board.get("index") if isinstance(board, dict) else None
        if not isinstance(board_index, int) or board_index >= len(hashboards):
            # Unknown / out-of-range chain index; skip rather than crash.
            return

        hb = hashboards[board_index]
        self._set_board_hashrate(hb, board.get("rate_real", 0))

        asic_num = board.get("asic_num")
        if isinstance(asic_num, int):
            hb.chips = asic_num

        temp = self._average_pcb_temp(board.get("temp_pcb"))
        if temp is not None:
            hb.temp = temp

        chip_temp = self._average_chip_temp(board.get("temp_chip"))
        if chip_temp is not None:
            hb.chip_temp = chip_temp

        hb.serial_number = board.get("sn") or None
        # Treat a chain with no live ASICs as missing so downstream consumers
        # can distinguish a populated-but-broken board from an empty slot
        # (DG-Home1 ships with 1 of 4 chains populated).
        hb.missing = not (isinstance(asic_num, int) and asic_num > 0)

    def _set_board_hashrate(self, hb: HashBoard, rate_real: float | int) -> None:
        """Convert ``rate_real`` (MH/s on Elphapex) into the algo's default unit."""
        try:
            hb.hashrate = self.algo.hashrate(
                rate=rate_real,
                unit=self.algo.unit.MH,  # type: ignore[attr-defined]
            ).into(
                self.algo.unit.default  # type: ignore[attr-defined]
            )
        except (TypeError, ValueError):
            pass

    @staticmethod
    def _average_pcb_temp(temps: object) -> float | None:
        """Average non-zero PCB temperature readings, or ``None`` if empty."""
        if not isinstance(temps, list):
            return None
        readings = [t for t in temps if isinstance(t, (int, float)) and t != 0]
        if not readings:
            return None
        return sum(readings) / len(readings)

    @staticmethod
    def _average_chip_temp(temps: object) -> float | None:
        """Average ``temp_chip`` entries (millidegree strings on Elphapex)."""
        # Inactive chains report empty strings here; a single ``None`` chain
        # on DG-Home1 used to trigger ``ZeroDivisionError`` in the legacy
        # parser.
        if not isinstance(temps, list):
            return None
        readings: list[float] = []
        for raw in temps:
            if raw in (None, ""):
                continue
            try:
                readings.append(int(raw) / 1000)
            except (TypeError, ValueError):
                continue
        if not readings:
            return None
        return sum(readings) / len(readings)

    async def _get_fault_light(
        self, web_get_blink_status: dict | None = None
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
        self, web_stats: dict | None = None
    ) -> AlgoHashRateType | None:
        if web_stats is None:
            try:
                web_stats = await self.web.stats()
            except APIError:
                pass

        if web_stats is not None:
            try:
                expected_rate = web_stats["STATS"][1]["total_rateideal"]
                try:
                    rate_unit = web_stats["STATS"][1]["rate_unit"]
                except KeyError:
                    rate_unit = "MH"
                return self.algo.hashrate(
                    rate=float(expected_rate), unit=self.algo.unit.from_str(rate_unit)
                ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except LookupError:
                pass
        return None

    async def _is_mining(self, web_get_miner_conf: dict | None = None) -> bool | None:
        if web_get_miner_conf is None:
            try:
                web_get_miner_conf = await self.web.get_miner_conf()
            except APIError:
                pass

        if web_get_miner_conf is not None:
            try:
                if str(web_get_miner_conf["fc-work-mode"]).isdigit():
                    return (
                        False if int(web_get_miner_conf["fc-work-mode"]) == 1 else True
                    )
                return False
            except LookupError:
                pass
        return None

    async def _get_uptime(self, web_summary: dict | None = None) -> int | None:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                return int(web_summary["SUMMARY"][1]["elapsed"])
            except LookupError:
                pass
        return None

    async def _get_fans(self, web_stats: dict | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if web_stats is None:
            try:
                web_stats = await self.web.stats()
            except APIError:
                pass

        fans = [Fan() for _ in range(self.expected_fans)]
        if web_stats is not None:
            for fan_n in range(self.expected_fans):
                try:
                    fans[fan_n].speed = int(web_stats["STATS"][0]["fan"][fan_n])
                except LookupError:
                    pass

        return fans

    async def _get_pools(self, web_pools: dict | None = None) -> list[PoolMetrics]:
        if web_pools is None:
            try:
                web_pools = await self.web.pools()
            except APIError:
                return []

        if web_pools is None:
            return []

        active_pool_index = None
        highest_priority = float("inf")

        for pool_info in web_pools["POOLS"]:
            if (
                pool_info.get("status") == "Alive"
                and pool_info.get("priority", float("inf")) < highest_priority
            ):
                highest_priority = pool_info["priority"]
                active_pool_index = pool_info["index"]

        pools_data = []
        try:
            for pool_info in web_pools["POOLS"]:
                url = pool_info.get("url")
                pool_url = PoolUrl.from_str(url) if url else None
                pool_data = PoolMetrics(
                    accepted=pool_info.get("accepted"),
                    rejected=pool_info.get("rejected"),
                    get_failures=pool_info.get("stale"),
                    remote_failures=pool_info.get("discarded"),
                    active=pool_info.get("index") == active_pool_index,
                    alive=pool_info.get("status") == "Alive",
                    url=pool_url,
                    user=pool_info.get("user"),
                    index=pool_info.get("index"),
                )
                pools_data.append(pool_data)
        except LookupError:
            pass
        return pools_data
