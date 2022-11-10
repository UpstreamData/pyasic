#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import re

from pyasic.config import MinerConfig
from pyasic.data import HashBoard, MinerData
from pyasic.miners._backends import CGMiner  # noqa - Ignore access to _module
from pyasic.settings import PyasicSettings


class CGMinerA8X(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip

    async def check_light(self) -> bool:
        if self.light:
            return self.light
        data = await self.api.ascset(0, "led", "1-255")
        if data["STATUS"][0]["Msg"] == "ASC 0 set info: LED[1]":
            return True
        return False

    async def fault_light_on(self) -> bool:
        data = await self.api.ascset(0, "led", "1-1")
        if data["STATUS"][0]["Msg"] == "ASC 0 set OK":
            return True
        return False

    async def fault_light_off(self) -> bool:
        data = await self.api.ascset(0, "led", "1-0")
        if data["STATUS"][0]["Msg"] == "ASC 0 set OK":
            return True
        return False

    async def reboot(self) -> bool:
        if (await self.api.restart())["STATUS"] == "RESTART":
            return True
        return False

    async def stop_mining(self) -> bool:
        return False

    async def resume_mining(self) -> bool:
        return False

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        """Configures miner with yaml config."""
        raise NotImplementedError
        logging.debug(f"{self}: Sending config.")
        conf = config.as_avalon(user_suffix=user_suffix)
        data = await self.api.ascset(
            0, "setpool", f"root,root,{conf}"
        )  # this should work but doesn't
        return data

    async def get_mac(self) -> str:
        mac = None
        version = await self.api.version()
        if version:
            if "VERSION" in version.keys():
                if "MAC" in version["VERSION"][0].keys():
                    base_mac = version["VERSION"][0]["MAC"].upper()
                    # parse the MAC into a recognizable form
                    mac = ":".join(
                        [base_mac[i : (i + 2)] for i in range(0, len(base_mac), 2)]
                    )
        return mac

    async def get_data(self, allow_warning: bool = True):
        data = MinerData(
            ip=str(self.ip),
            ideal_chips=self.nominal_chips * self.ideal_hashboards,
            ideal_hashboards=self.ideal_hashboards,
            hashboards=[
                HashBoard(slot=i, expected_chips=self.nominal_chips)
                for i in range(self.ideal_hashboards)
            ],
        )

        model = await self.get_model()
        mac = None

        if model:
            data.model = model

        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            miner_data = await self.api.multicommand(
                "version", "summary", "pools", "stats", allow_warning=allow_warning
            )
            if miner_data:
                break
        if not miner_data:
            hostname = await self.get_hostname()
            mac = await self.get_mac()

            if hostname and not hostname == "?":
                data.hostname = hostname
            elif mac:
                data.hostname = f"Avalon{mac.replace(':', '')[-6:]}"
            if mac:
                data.mac = mac
            return data

        data.fault_light = await self.check_light()

        summary = miner_data.get("summary")
        version = miner_data.get("version")
        pools = miner_data.get("pools")
        stats = miner_data.get("stats")

        if summary:
            hr = summary[0].get("SUMMARY")
            if hr:
                if len(hr) > 0:
                    hr = hr[0].get("MHS 1m")
                    if hr:
                        data.hashrate = round(hr / 1000000, 2)

        if version:
            if "VERSION" in version[0].keys():
                if "MAC" in version[0]["VERSION"][0].keys():
                    base_mac = version[0]["VERSION"][0]["MAC"].upper()
                    # parse the MAC into a recognizable form
                    mac = ":".join(
                        [base_mac[i : (i + 2)] for i in range(0, len(base_mac), 2)]
                    )

        if stats:
            stats_data = stats[0].get("STATS")
            if stats_data:
                for key in stats_data[0].keys():
                    if key.startswith("MM ID"):
                        raw_data = self.parse_stats(stats_data[0][key])
                        for fan in range(self.fan_count):
                            if f"Fan{fan+1}" in raw_data:
                                setattr(
                                    data,
                                    f"fan_{fan+1}",
                                    int(raw_data[f"Fan{fan+1}"]),
                                )
                        for board in range(self.ideal_hashboards):
                            chip_temp = raw_data.get("MTmax")
                            if chip_temp:
                                data.hashboards[board].chip_temp = chip_temp[board]

                            temp = raw_data.get("MTavg")
                            if temp:
                                data.hashboards[board].temp = temp[board]

                            chips = raw_data.get(f"PVT_T{board}")
                            if chips:
                                data.hashboards[board].chips = len(
                                    [item for item in chips if not item == "0"]
                                )

        if pools:
            pool_1 = None
            pool_2 = None
            pool_1_user = None
            pool_2_user = None
            pool_1_quota = 1
            pool_2_quota = 1
            quota = 0
            for pool in pools[0].get("POOLS"):
                if not pool_1_user:
                    pool_1_user = pool.get("User")
                    pool_1 = pool["URL"]
                    pool_1_quota = pool["Quota"]
                elif not pool_2_user:
                    pool_2_user = pool.get("User")
                    pool_2 = pool["URL"]
                    pool_2_quota = pool["Quota"]
                if not pool.get("User") == pool_1_user:
                    if not pool_2_user == pool.get("User"):
                        pool_2_user = pool.get("User")
                        pool_2 = pool["URL"]
                        pool_2_quota = pool["Quota"]
            if pool_2_user and not pool_2_user == pool_1_user:
                quota = f"{pool_1_quota}/{pool_2_quota}"

            if pool_1:
                pool_1 = pool_1.replace("stratum+tcp://", "").replace(
                    "stratum2+tcp://", ""
                )
                data.pool_1_url = pool_1

            if pool_1_user:
                data.pool_1_user = pool_1_user

            if pool_2:
                pool_2 = pool_2.replace("stratum+tcp://", "").replace(
                    "stratum2+tcp://", ""
                )
                data.pool_2_url = pool_2

            if pool_2_user:
                data.pool_2_user = pool_2_user

            if quota:
                data.pool_split = str(quota)

        hostname = await self.get_hostname()

        if mac:
            data.mac = mac
        else:
            mac = await self.get_mac()
            if mac:
                data.mac = mac
        if hostname and not hostname == "?":
            data.hostname = hostname
        elif mac:
            data.hostname = f"Avalon{mac.replace(':', '')[-6:]}"

        return data

    @staticmethod
    def parse_stats(stats):
        _stats_items = re.findall(".+?\[*?]", stats)
        stats_items = []
        stats_dict = {}
        for item in _stats_items:
            if ":" in item:
                data = item.replace("]", "").split("[")
                data_list = [i.split(": ") for i in data[1].strip().split(", ")]
                data_dict = {}
                for key, val in [tuple(item) for item in data_list]:
                    data_dict[key] = val
                raw_data = [data[0].strip(), data_dict]
            else:
                raw_data = [
                    value
                    for value in item.replace("[", " ")
                    .replace("]", " ")
                    .split(" ")[:-1]
                    if value != ""
                ]
                if len(raw_data) == 1:
                    raw_data.append("")
            if raw_data[0] == "":
                raw_data = raw_data[1:]

            if len(raw_data) == 2:
                stats_dict[raw_data[0]] = raw_data[1]
            else:
                stats_dict[raw_data[0]] = raw_data[1:]
            stats_items.append(raw_data)

        return stats_dict
