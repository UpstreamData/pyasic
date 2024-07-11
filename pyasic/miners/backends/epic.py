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

from pathlib import Path
from typing import List, Optional

from pyasic.config import MinerConfig
from pyasic.data import AlgoHashRate, Fan, HashBoard, HashUnit
from pyasic.data.error_codes import MinerErrorData, X19Error
from pyasic.data.pools import PoolMetrics
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.miners.device.firmware import ePICFirmware
from pyasic.web.epic import ePICWebAPI

EPIC_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_network", "network")],
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
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [
                WebAPICommand("web_summary", "summary"),
                WebAPICommand("web_capabilities", "capabilities"),
            ],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_summary", "summary")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [WebAPICommand("web_summary", "summary")],
        ),
    }
)


class ePIC(ePICFirmware):
    """Handler for miners with the ePIC board"""

    _web_cls = ePICWebAPI
    web: ePICWebAPI

    data_locations = EPIC_DATA_LOC

    supports_shutdown = True

    async def get_config(self) -> MinerConfig:
        summary = None
        try:
            summary = await self.web.summary()
        except APIError as e:
            logger.warning(e)
        except LookupError:
            pass

        if summary is not None:
            cfg = MinerConfig.from_epic(summary)
        else:
            cfg = MinerConfig()

        self.config = cfg
        return self.config

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config
        conf = self.config.as_epic(user_suffix=user_suffix)

        try:
            # Temps
            if not conf.get("temps", {}) == {}:
                await self.web.set_shutdown_temp(conf["temps"]["shutdown"])
                await self.web.set_critical_temp(conf["temps"]["critical"])
            # Fans
            # set with sub-keys instead of conf["fans"] because sometimes both can be set
            if not conf["fans"].get("Manual", {}) == {}:
                await self.web.set_fan({"Manual": conf["fans"]["Manual"]})
            elif not conf["fans"].get("Auto", {}) == {}:
                await self.web.set_fan({"Auto": conf["fans"]["Auto"]})

            # Mining Mode -- Need to handle that you may not be able to change while miner is tuning
            if conf["ptune"].get("enabled", True):
                await self.web.set_ptune_enable(True)
                await self.web.set_ptune_algo(conf["ptune"])

            ## Pools
            await self.web.set_pools(conf["pools"])
        except APIError:
            pass

    async def restart_backend(self) -> bool:
        data = await self.web.restart_epic()
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

    async def _get_mac(self, web_network: dict = None) -> Optional[str]:
        if web_network is None:
            try:
                web_network = await self.web.network()
            except APIError:
                pass

        if web_network is not None:
            try:
                for network in web_network:
                    mac = web_network[network]["mac_address"]
                    return mac
            except KeyError:
                pass

    async def _get_hostname(self, web_summary: dict = None) -> Optional[str]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                hostname = web_summary["Hostname"]
                return hostname
            except KeyError:
                pass

    async def _get_wattage(self, web_summary: dict = None) -> Optional[int]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                wattage = web_summary["Power Supply Stats"]["Input Power"]
                wattage = round(wattage)
                return wattage
            except KeyError:
                pass

    async def _get_hashrate(self, web_summary: dict = None) -> Optional[AlgoHashRate]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                hashrate = 0
                if web_summary["HBs"] is not None:
                    for hb in web_summary["HBs"]:
                        hashrate += hb["Hashrate"][0]
                    return AlgoHashRate.SHA256(hashrate, HashUnit.SHA256.MH).into(
                        HashUnit.SHA256.TH
                    )
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_expected_hashrate(
        self, web_summary: dict = None
    ) -> Optional[AlgoHashRate]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                hashrate = 0
                if web_summary.get("HBs") is not None:
                    for hb in web_summary["HBs"]:
                        if hb["Hashrate"][1] == 0:
                            ideal = 1.0
                        else:
                            ideal = hb["Hashrate"][1] / 100

                        hashrate += hb["Hashrate"][0] / ideal
                    return AlgoHashRate.SHA256(hashrate, HashUnit.SHA256.MH).into(
                        self.algo.unit.default
                    )
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_fw_ver(self, web_summary: dict = None) -> Optional[str]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                fw_ver = web_summary["Software"]
                fw_ver = fw_ver.split(" ")[1].replace("v", "")
                return fw_ver
            except KeyError:
                pass

    async def _get_fans(self, web_summary: dict = None) -> List[Fan]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        fans = []

        if web_summary is not None:
            for fan in web_summary["Fans Rpm"]:
                try:
                    fans.append(Fan(web_summary["Fans Rpm"][fan]))
                except (LookupError, ValueError, TypeError):
                    fans.append(Fan())
        return fans

    async def _get_hashboards(
        self, web_summary: dict = None, web_capabilities: dict = None
    ) -> List[HashBoard]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_capabilities is None:
            try:
                web_capabilities = await self.web.capabilities()
            except APIError:
                pass

        tuned = True
        active = False
        if web_summary is not None:
            tuner_running = web_summary["PerpetualTune"]["Running"]
            if tuner_running:
                active = True
                algo_info = web_summary["PerpetualTune"]["Algorithm"]
                if algo_info.get("VoltageOptimizer") is not None:
                    tuned = algo_info["VoltageOptimizer"].get("Optimized")
                elif algo_info.get("BoardTune") is not None:
                    tuned = algo_info["BoardTune"].get("Optimized")
                else:
                    tuned = algo_info["ChipTune"].get("Optimized")

            # To be extra detailed, also ensure the miner is in "Mining" state
            tuned = tuned and web_summary["Status"]["Operating State"] == "Mining"
            active = active and web_summary["Status"]["Operating State"] == "Mining"

        hb_list = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]
        if web_summary is not None and web_capabilities is not None:
            if web_summary.get("HBs") is not None:
                for hb in web_summary["HBs"]:
                    if web_capabilities.get("Performance Estimator") is not None:
                        num_of_chips = web_capabilities["Performance Estimator"][
                            "Chip Count"
                        ]
                    else:
                        num_of_chips = self.expected_chips
                    if web_capabilities.get("Board Serial Numbers") is not None:
                        if hb["Index"] < len(web_capabilities["Board Serial Numbers"]):
                            hb_list[hb["Index"]].serial_number = web_capabilities[
                                "Board Serial Numbers"
                            ][hb["Index"]]
                    hashrate = hb["Hashrate"][0]
                    # Update the Hashboard object
                    hb_list[hb["Index"]].missing = False
                    hb_list[hb["Index"]].hashrate = AlgoHashRate.SHA256(
                        hashrate, HashUnit.SHA256.MH
                    ).into(self.algo.unit.default)
                    hb_list[hb["Index"]].chips = num_of_chips
                    hb_list[hb["Index"]].temp = hb["Temperature"]
                    hb_list[hb["Index"]].tuned = tuned
                    hb_list[hb["Index"]].active = active
                    hb_list[hb["Index"]].voltage = hb["Input Voltage"]
            return hb_list

    async def _is_mining(self, web_summary, *args, **kwargs) -> Optional[bool]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass
        if web_summary is not None:
            try:
                op_state = web_summary["Status"]["Operating State"]
                return not op_state == "Idling"
            except KeyError:
                pass

    async def _get_uptime(self, web_summary: dict = None) -> Optional[int]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                uptime = web_summary["Session"]["Uptime"]
                return uptime
            except KeyError:
                pass
        return None

    async def _get_fault_light(self, web_summary: dict = None) -> Optional[bool]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        if web_summary is not None:
            try:
                light = web_summary["Misc"]["Locate Miner State"]
                return light
            except KeyError:
                pass
        return False

    async def _get_errors(self, web_summary: dict = None) -> List[MinerErrorData]:
        if not web_summary:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        errors = []
        if web_summary is not None:
            try:
                error = web_summary["Status"]["Last Error"]
                if error is not None:
                    errors.append(X19Error(str(error)))
                return errors
            except KeyError:
                pass
        return errors

    async def _get_pools(self, web_summary: dict = None) -> List[PoolMetrics]:
        if web_summary is None:
            try:
                web_summary = await self.web.summary()
            except APIError:
                pass

        pool_data = []
        try:
            if web_summary is not None:
                if (
                    web_summary.get("Session") is not None
                    and web_summary.get("Stratum") is not None
                ):
                    pool_data.append(
                        PoolMetrics(
                            accepted=web_summary["Session"].get("Accepted"),
                            rejected=web_summary["Session"].get("Rejected"),
                            get_failures=0,
                            remote_failures=0,
                            active=web_summary["Stratum"].get("IsPoolConnected"),
                            alive=web_summary["Stratum"].get("IsPoolConnected"),
                            url=web_summary["Stratum"].get("Current Pool"),
                            user=web_summary["Stratum"].get("Current User"),
                            index=web_summary["Stratum"].get("Config Id"),
                        )
                    )
                return pool_data
        except LookupError:
            pass

    async def upgrade_firmware(self, file: Path | str, keep_settings: bool = True) -> bool:

        """
        Upgrade the firmware of the ePIC miner device.

        Args:
            file (Path | str): The local file path of the firmware to be uploaded.
            keep_settings (bool): Whether to keep the current settings after the update.

        Returns:
            bool: Whether the firmware update succeeded.
        """
        return await self.web.system_update(file=file, keep_settings=keep_settings)