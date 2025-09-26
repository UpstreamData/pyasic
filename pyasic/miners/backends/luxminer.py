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

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModePreset
from pyasic.data import Fan, HashBoard
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm import AlgoHashRateType
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
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [
                RPCAPICommand("rpc_config", "config"),
                RPCAPICommand("rpc_profiles", "profiles"),
            ],
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
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver", [RPCAPICommand("rpc_version", "version")]
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver", [RPCAPICommand("rpc_version", "version")]
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light", [RPCAPICommand("rpc_config", "config")]
        ),
    }
)


class LUXMiner(LuxOSFirmware):
    """Handler for LuxOS miners"""

    _rpc_cls = LUXMinerRPCAPI
    rpc: LUXMinerRPCAPI

    supports_shutdown = True
    supports_presets = True
    supports_autotuning = True

    data_locations = LUXMINER_DATA_LOC

    async def fault_light_on(self) -> bool:
        try:
            await self.rpc.ledset("red", "blink")
            return True
        except (APIError, LookupError):
            pass
        return False

    async def fault_light_off(self) -> bool:
        try:
            await self.rpc.ledset("red", "off")
            return True
        except (APIError, LookupError):
            pass
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_luxminer()

    async def restart_luxminer(self) -> bool:
        try:
            await self.rpc.resetminer()
            return True
        except (APIError, LookupError):
            pass
        return False

    async def stop_mining(self) -> bool:
        try:
            await self.rpc.sleep()
            return True
        except (APIError, LookupError):
            pass
        return False

    async def resume_mining(self) -> bool:
        try:
            await self.rpc.wakeup()
            return True
        except (APIError, LookupError):
            pass
        return False

    async def reboot(self) -> bool:
        try:
            await self.rpc.rebootdevice()
            return True
        except (APIError, LookupError):
            pass
        return False

    async def get_config(self) -> MinerConfig:
        data = await self.rpc.multicommand(
            "tempctrl", "fans", "pools", "groups", "config", "profiles"
        )
        return MinerConfig.from_luxos(
            rpc_tempctrl=data.get("tempctrl", [{}])[0],
            rpc_fans=data.get("fans", [{}])[0],
            rpc_pools=data.get("pools", [{}])[0],
            rpc_groups=data.get("groups", [{}])[0],
            rpc_config=data.get("config", [{}])[0],
            rpc_profiles=data.get("profiles", [{}])[0],
        )

    async def upgrade_firmware(self, *args, **kwargs) -> bool:
        """
        Upgrade the firmware on a LuxOS miner by calling the 'updaterun' API command.
        Returns:
            bool: True if the firmware upgrade was successfully initiated, False otherwise.
        """
        try:
            await self.rpc.updaterun()
            logging.info(f"{self.ip}: Firmware upgrade initiated successfully.")
            return True

        except APIError as e:
            logging.error(f"{self.ip}: Firmware upgrade failed: {e}")

        return False

    async def atm_enabled(self) -> bool | None:
        try:
            result = await self.rpc.atm()
            return result["ATM"][0]["Enabled"]
        except (APIError, LookupError):
            pass
        return None

    async def set_power_limit(self, wattage: int) -> bool:
        config = await self.get_config()

        # Check if we have preset mode with available presets
        if not hasattr(config.mining_mode, "available_presets"):
            logging.warning(f"{self} - Mining mode does not support presets")
            return False

        available_presets = getattr(config.mining_mode, "available_presets", [])
        if not available_presets:
            logging.warning(f"{self} - No available presets found")
            return False

        valid_presets = {
            preset.name: preset.power
            for preset in available_presets
            if preset.power is not None and preset.power <= wattage
        }

        if not valid_presets:
            logging.warning(f"{self} - No valid presets found for wattage {wattage}")
            return False

        # Set power to highest preset <= wattage
        # If ATM enabled, must disable it before setting power limit
        new_preset = max(valid_presets, key=lambda x: valid_presets[x])

        re_enable_atm = False
        try:
            if await self.atm_enabled():
                re_enable_atm = True
                await self.rpc.atmset(enabled=False)
            result = await self.rpc.profileset(new_preset)
            if re_enable_atm:
                await self.rpc.atmset(enabled=True)
        except APIError:
            raise
        except Exception as e:
            logging.warning(f"{self} - Failed to set power limit: {e}")
            return False

        if result["PROFILE"][0]["Profile"] == new_preset:
            return True
        else:
            return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(self, rpc_config: dict | None = None) -> str | None:
        if rpc_config is None:
            try:
                rpc_config = await self.rpc.config()
            except APIError:
                pass
        return None

        if rpc_config is not None:
            try:
                return rpc_config["CONFIG"][0]["MACAddr"].upper()
            except KeyError:
                pass

    async def _get_hashrate(
        self, rpc_summary: dict | None = None
    ) -> AlgoHashRateType | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass
        return None

        if rpc_summary is not None:
            try:
                return self.algo.hashrate(
                    rate=float(rpc_summary["SUMMARY"][0]["GHS 5s"]),
                    unit=self.algo.unit.GH,
                ).into(self.algo.unit.default)
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_hashboards(self, rpc_stats: dict | None = None) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=idx, expected_chips=self.expected_chips)
            for idx in range(self.expected_hashboards)
        ]

        if rpc_stats is None:
            try:
                rpc_stats = await self.rpc.stats()
            except APIError:
                pass
        if rpc_stats is not None:
            try:
                # TODO: bugged on S9 because of index issues, fix later.
                board_stats = rpc_stats["STATS"][1]
                for idx in range(3):
                    board_n = idx + 1
                    hashboards[idx].hashrate = self.algo.hashrate(
                        rate=float(board_stats[f"chain_rate{board_n}"]),
                        unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    )
                    hashboards[idx].chips = int(board_stats[f"chain_acn{board_n}"])
                    chip_temp_data = list(
                        filter(
                            lambda x: not x == 0,
                            map(int, board_stats[f"temp_chip{board_n}"].split("-")),
                        )
                    )
                    hashboards[idx].chip_temp = (
                        sum([chip_temp_data[0], chip_temp_data[3]]) / 2
                    )
                    board_temp_data = list(
                        filter(
                            lambda x: not x == 0,
                            map(int, board_stats[f"temp_pcb{board_n}"].split("-")),
                        )
                    )
                    hashboards[idx].temp = (
                        sum([board_temp_data[1], board_temp_data[2]]) / 2
                    )
                    hashboards[idx].missing = False
            except LookupError:
                pass
        return hashboards

    async def _get_wattage(self, rpc_power: dict | None = None) -> int | None:
        if rpc_power is None:
            try:
                rpc_power = await self.rpc.power()
            except APIError:
                pass
        return None

        if rpc_power is not None:
            try:
                return rpc_power["POWER"][0]["Watts"]
            except (LookupError, ValueError, TypeError):
                pass
        return None

    async def _get_wattage_limit(
        self, rpc_config: dict | None = None, rpc_profiles: dict | None = None
    ) -> int | None:
        if rpc_config is None or rpc_profiles is None:
            return None
        try:
            active_preset = MiningModePreset.get_active_preset_from_luxos(
                rpc_config, rpc_profiles
            )
            return active_preset.power
        except (LookupError, ValueError, TypeError):
            pass
        return None

    async def _get_fans(self, rpc_fans: dict | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_fans is None:
            try:
                rpc_fans = await self.rpc.fans()
            except APIError:
                pass

        fans = []

        if rpc_fans is not None:
            for fan in range(self.expected_fans):
                try:
                    fans.append(Fan(speed=rpc_fans["FANS"][fan]["RPM"]))
                except (LookupError, ValueError, TypeError):
                    fans.append(Fan())
        return fans

    async def _get_expected_hashrate(
        self, rpc_stats: dict | None = None
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

    async def _get_uptime(self, rpc_stats: dict | None = None) -> int | None:
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

    async def _get_fw_ver(self, rpc_version: dict | None = None) -> str | None:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                return rpc_version["VERSION"][0]["Miner"]
            except LookupError:
                pass
        return None

    async def _get_api_ver(self, rpc_version: dict | None = None) -> str | None:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                pass

        if rpc_version is not None:
            try:
                return rpc_version["VERSION"][0]["API"]
            except LookupError:
                pass
        return None

    async def _get_fault_light(self, rpc_config: dict | None = None) -> bool | None:
        if rpc_config is None:
            try:
                rpc_config = await self.rpc.config()
            except APIError:
                pass

        if rpc_config is not None:
            try:
                return not rpc_config["CONFIG"][0]["RedLed"] == "off"
            except LookupError:
                pass
        return None

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
