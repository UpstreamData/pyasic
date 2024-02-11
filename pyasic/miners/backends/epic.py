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
from pyasic.data import Fan, HashBoard
from pyasic.data.error_codes import MinerErrorData, X19Error
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
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
    }
)


class ePIC(BaseMiner):
    """Handler for miners with the ePIC board"""

    _web_cls = ePICWebAPI
    web: ePICWebAPI

    firmware = "ePIC"

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
            # Fans
            # set with sub-keys instead of conf["fans"] because sometimes both can be set
            if not conf["fans"].get("Manual", {}) == {}:
                await self.web.set_fan({"Manual": conf["fans"]["Manual"]})
            elif not conf["fans"].get("Auto", {}) == {}:
                await self.web.set_fan({"Auto": conf["fans"]["Auto"]})

            # Mining Mode -- Need to handle that you may not be able to change while miner is tuning
            if conf["ptune"].get("enabled", True):
                await self.web.set_ptune_enable(True)
                await self.web.set_ptune_algo(**conf["ptune"])

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

    async def _get_hashrate(self, web_summary: dict = None) -> Optional[float]:
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
                    return round(float(float(hashrate / 1000000)), 2)
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_expected_hashrate(self, web_summary: dict = None) -> Optional[float]:
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
                    return round(float(float(hashrate / 1000000)), 2)
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

        if web_capabilities is not None:
            try:
                web_capabilities = await self.web.capabilities()
            except APIError:
                pass

        hb_list = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]
        if web_summary.get("HBs") is not None:
            for hb in web_summary["HBs"]:
                num_of_chips = web_capabilities["Performance Estimator"]["Chip Count"]
                hashrate = hb["Hashrate"][0]
                # Update the Hashboard object
                hb_list[hb["Index"]].missing = False
                hb_list[hb["Index"]].hashrate = round(hashrate / 1000000, 2)
                hb_list[hb["Index"]].chips = num_of_chips
                hb_list[hb["Index"]].temp = hb["Temperature"]
        return hb_list

    async def _is_mining(self, *args, **kwargs) -> Optional[bool]:
        return None

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
