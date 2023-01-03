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

from typing import List, Optional

from pyasic.data import HashBoard, MinerData
from pyasic.miners._backends import Hiveon  # noqa - Ignore access to _module
from pyasic.miners._types import T9  # noqa - Ignore access to _module
from pyasic.settings import PyasicSettings
from pyasic.errors import APIError


class HiveonT9(Hiveon, T9):
    def __init__(self, ip: str, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, api_ver=api_ver)
        self.ip = ip
        self.pwd = "admin"

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def get_mac(self):
        try:
            mac = (
                (await self.send_ssh_command("cat /sys/class/net/eth0/address"))
                .strip()
                .upper()
            )
            return mac
        except (TypeError, ValueError):
            pass

    async def get_hashboards(self, api_stats: dict = None) -> List[HashBoard]:
        board_map = {
            0: [2, 9, 10],
            1: [3, 11, 12],
            2: [4, 13, 14],
        }
        hashboards = []

        for board in board_map:
            hashboard = HashBoard(slot=board, expected_chips=self.nominal_chips)
            hashrate = 0
            chips = 0
            for chipset in board_map[board]:
                if hashboard.chip_temp == -1:
                    try:
                        hashboard.board_temp = api_stats["STATS"][1][f"temp{chipset}"]
                        hashboard.chip_temp = api_stats["STATS"][1][f"temp2_{chipset}"]
                        hashrate += api_stats["STATS"][1][f"chain_rate{chipset}"]
                        chips += api_stats["STATS"][1][f"chain_acn{chipset}"]
                    except (KeyError, IndexError):
                        pass
                    else:
                        hashboard.missing = False
            hashboard.hashrate = hashrate
            hashboard.chips = chips
            hashboards.append(hashboard)

        return hashboards

    async def get_wattage(self, api_stats: dict = None) -> Optional[int]:
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass

        if api_stats:
            boards = api_stats.get("STATS")
            try:
                wattage_raw = boards[1]["chain_power"]
            except (KeyError, IndexError):
                pass
            else:
                # parse wattage position out of raw data
                return round(float(wattage_raw.split(" ")[0]))

    async def get_env_temp(self, api_stats: dict = None) -> Optional[float]:
        env_temp_list = []
        board_map = {
            0: [2, 9, 10],
            1: [3, 11, 12],
            2: [4, 13, 14],
        }
        if not api_stats:
            try:
                api_stats = await self.api.stats()
            except APIError:
                pass
        if api_stats:
            for board in board_map.values():
                for chipset in board:
                    try:
                        env_temp = api_stats["STATS"][1][f"temp3_{chipset}"]
                        if not env_temp == 0:
                            env_temp_list.append(int(env_temp))
                    except (KeyError, IndexError):
                        pass

            if not env_temp_list == []:
                return round(float(sum(env_temp_list) / len(env_temp_list)), 2)

    async def _get_data(self, allow_warning: bool) -> dict:
        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            try:
                miner_data = await self.api.multicommand(
                    "summary",
                    "pools",
                    "version",
                    "devdetails",
                    "stats",
                    allow_warning=allow_warning,
                )
            except APIError:
                pass
            if miner_data:
                break
        if miner_data:
            summary = miner_data.get("summary")
            if summary:
                summary = summary[0]
            pools = miner_data.get("pools")
            if pools:
                pools = pools[0]
            version = miner_data.get("version")
            if version:
                version = version[0]
            devdetails = miner_data.get("devdetails")
            if devdetails:
                devdetails = devdetails[0]
            stats = miner_data.get("stats")
            if stats:
                stats = stats[0]
        else:
            summary, pools, devdetails, version, stats = (None for _ in range(5))

        data = {  # noqa - Ignore dictionary could be re-written
            # ip - Done at start
            # datetime - Done auto
            "mac": await self.get_mac(),
            "model": await self.get_model(api_devdetails=devdetails),
            # make - Done at start
            # api_ver - Done at end
            # fw_ver - Done at end
            "hostname": await self.get_hostname(),
            "hashrate": await self.get_hashrate(api_summary=summary),
            "hashboards": await self.get_hashboards(api_stats=stats),
            # ideal_hashboards - Done at start
            "env_temp": await self.get_env_temp(api_stats=stats),
            "wattage": await self.get_wattage(api_stats=stats),
            "wattage_limit": await self.get_wattage_limit(),
            # fan_1 - Done at end
            # fan_2 - Done at end
            # fan_3 - Done at end
            # fan_4 - Done at end
            # fan_psu - Done at end
            # ideal_chips - Done at start
            # pool_split - Done at end
            # pool_1_url - Done at end
            # pool_1_user - Done at end
            # pool_2_url - Done at end
            # pool_2_user - Done at end
            "errors": await self.get_errors(),
            "fault_light": await self.get_fault_light(),
        }

        data["api_ver"], data["fw_ver"] = await self.get_version(api_version=version)
        fan_data = await self.get_fans()

        data["fan_1"] = fan_data.fan_speeds.fan_1  # noqa
        data["fan_2"] = fan_data.fan_speeds.fan_2  # noqa
        data["fan_3"] = fan_data.fan_speeds.fan_3  # noqa
        data["fan_4"] = fan_data.fan_speeds.fan_4  # noqa

        data["fan_psu"] = fan_data.psu_fan_speeds.psu_fan  # noqa

        pools_data = await self.get_pools(api_pools=pools)
        data["pool_1_url"] = pools_data[0]["pool_1_url"]
        data["pool_1_user"] = pools_data[0]["pool_1_user"]
        if len(pools_data) > 1:
            data["pool_2_url"] = pools_data[1]["pool_1_url"]
            data["pool_2_user"] = pools_data[1]["pool_1_user"]
            data["pool_split"] = f"{pools_data[0]['quota']}/{pools_data[1]['quota']}"
        else:
            try:
                data["pool_2_url"] = pools_data[0]["pool_1_url"]
                data["pool_2_user"] = pools_data[0]["pool_1_user"]
                data["quota"] = "0"
            except KeyError:
                pass

        return data
