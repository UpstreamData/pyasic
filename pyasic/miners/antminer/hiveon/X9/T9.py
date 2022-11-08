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

from pyasic.miners._backends import Hiveon  # noqa - Ignore access to _module
from pyasic.miners._types import T9  # noqa - Ignore access to _module

from pyasic.data import MinerData, HashBoard
from pyasic.settings import PyasicSettings


class HiveonT9(Hiveon, T9):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ip
        self.pwd = "admin"

    async def get_mac(self):
        mac = (
            (await self.send_ssh_command("cat /sys/class/net/eth0/address"))
            .strip()
            .upper()
        )
        return mac

    async def get_data(self, allow_warning: bool = False) -> MinerData:
        """Get data from the miner.

        Returns:
            A [`MinerData`][pyasic.data.MinerData] instance containing the miners data.
        """
        data = MinerData(
            ip=str(self.ip),
            ideal_chips=self.nominal_chips * self.ideal_hashboards,
            ideal_hashboards=self.ideal_hashboards,
        )

        board_offset = -1
        fan_offset = -1

        model = await self.get_model()
        hostname = await self.get_hostname()
        mac = await self.get_mac()
        errors = await self.get_errors()

        if model:
            data.model = model

        if hostname:
            data.hostname = hostname

        if mac:
            data.mac = mac

        if errors:
            for error in errors:
                data.errors.append(error)

        data.fault_light = await self.check_light()

        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            miner_data = await self.api.multicommand(
                "summary", "pools", "stats", allow_warning=allow_warning
            )
            if miner_data:
                break

        if not miner_data:
            return data

        summary = miner_data.get("summary")[0]
        pools = miner_data.get("pools")[0]
        stats = miner_data.get("stats")[0]

        if summary:
            hr = summary.get("SUMMARY")
            if hr:
                if len(hr) > 0:
                    hr = hr[0].get("GHS 1m")
                    if hr:
                        data.hashrate = round(hr / 1000, 2)

        if stats:
            boards = stats.get("STATS")
            if boards:
                if len(boards) > 0:
                    if "chain_power" in boards[1].keys():
                        data.wattage = round(
                            float(boards[1]["chain_power"].split(" ")[0])
                        )

                    board_map = {
                        0: [2, 9, 10],
                        1: [3, 11, 12],
                        2: [4, 13, 14],
                    }

                    env_temp_list = []

                    for board in board_map.keys():
                        hashboard = HashBoard(
                            slot=board, expected_chips=self.nominal_chips
                        )
                        chips = 0
                        hashrate = 0
                        chip_temp = 0
                        board_temp = 0
                        for chipset in board_map[board]:
                            if chip_temp == 0:
                                if f"temp{chipset}" in boards[1].keys():
                                    board_temp = boards[1][f"temp{chipset}"]
                                    chip_temp = boards[1][f"temp2_{chipset}"]
                                    if f"temp3_{chipset}" in boards[1].keys():
                                        env_temp = boards[1][f"temp3_{chipset}"]
                                        if not env_temp == 0:
                                            env_temp_list.append(int(env_temp))

                            hashrate += boards[1][f"chain_rate{chipset}"]
                            chips += boards[1][f"chain_acn{chipset}"]
                        hashboard.hashrate = hashrate
                        hashboard.chips = chips
                        hashboard.temp = board_temp
                        hashboard.chip_temp = chip_temp
                        hashboard.missing = True
                        if chips and chips > 0:
                            hashboard.missing = False
                        data.hashboards.append(hashboard)

                    if not env_temp_list == []:
                        data.env_temp = sum(env_temp_list) / len(env_temp_list)

        if stats:
            temp = stats.get("STATS")
            if temp:
                if len(temp) > 1:
                    for fan_num in range(1, 8, 4):
                        for _f_num in range(4):
                            f = temp[1].get(f"fan{fan_num + _f_num}")
                            if f and not f == 0 and fan_offset == -1:
                                fan_offset = fan_num
                    if fan_offset == -1:
                        fan_offset = 1
                    for fan in range(self.fan_count):
                        setattr(
                            data, f"fan_{fan + 1}", temp[1].get(f"fan{fan_offset+fan}")
                        )

        if pools:
            pool_1 = None
            pool_2 = None
            pool_1_user = None
            pool_2_user = None
            pool_1_quota = 1
            pool_2_quota = 1
            quota = 0
            for pool in pools.get("POOLS"):
                if not pool.get("User") == "*":
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

        return data
