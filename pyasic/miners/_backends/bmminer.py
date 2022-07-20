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

import ipaddress
import logging
from typing import Union


from pyasic.API.bmminer import BMMinerAPI
from pyasic.miners import BaseMiner

from pyasic.data import MinerData

from pyasic.settings import PyasicSettings


class BMMiner(BaseMiner):
    """Base handler for BMMiner based miners."""

    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BMMinerAPI(ip)
        self.api_type = "BMMiner"
        self.uname = "root"
        self.pwd = "admin"

    async def get_model(self) -> Union[str, None]:
        """Get miner model.

        Returns:
            Miner model or None.
        """
        # check if model is cached
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        # get devdetails data
        version_data = await self.api.devdetails()

        # if we get data back, parse it for model
        if version_data:
            # handle Antminer BMMiner as a base
            self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        # if we don't get devdetails, log a failed attempt
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_hostname(self) -> str:
        """Get miner hostname.

        Returns:
            The hostname of the miner as a string or "?"
        """
        if self.hostname:
            return self.hostname
        try:
            # open an ssh connection
            async with (await self._get_ssh_connection()) as conn:
                # if we get the connection, check hostname
                if conn is not None:
                    # get output of the hostname file
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()

                    # return hostname data
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    self.hostname = host
                    return self.hostname
                else:
                    # return ? if we fail to get hostname with no ssh connection
                    logging.warning(f"Failed to get hostname for miner: {self}")
                    return "?"
        except Exception:
            # return ? if we fail to get hostname with an exception
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def send_ssh_command(self, cmd: str) -> Union[str, None]:
        """Send a command to the miner over ssh.

        Parameters:
            cmd: The command to run.

        Returns:
            Result of the command or None.
        """
        result = None

        # open an ssh connection
        async with (await self._get_ssh_connection()) as conn:
            # 3 retries
            for i in range(3):
                try:
                    # run the command and get the result
                    result = await conn.run(cmd)
                    result = result.stdout

                except Exception as e:
                    # if the command fails, log it
                    logging.warning(f"{self} command {cmd} error: {e}")

                    # on the 3rd retry, return None
                    if i == 3:
                        return
                    continue
        # return the result, either command output or None
        return result

    async def get_config(self) -> Union[list, None]:
        """Get the pool configuration of the miner.

        Returns:
             Pool config data or None.
        """
        # get pool data
        pools = await self.api.pools()
        pool_data = []

        # ensure we got pool data
        if not pools:
            return

        # parse all the pools
        for pool in pools["POOLS"]:
            pool_data.append({"url": pool["URL"], "user": pool["User"], "pwd": "123"})
        return pool_data

    async def reboot(self) -> bool:
        """Reboot the miner.

        Returns:
            The result of rebooting the miner.
        """
        logging.debug(f"{self}: Sending reboot command.")
        _ret = await self.send_ssh_command("reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def get_data(self) -> MinerData:
        """Get data from the miner.

        Returns:
            A [`MinerData`][pyasic.data.MinerData] instance containing the miners data.
        """
        data = MinerData(ip=str(self.ip), ideal_chips=self.nominal_chips * 3)

        board_offset = -1
        fan_offset = -1

        model = await self.get_model()
        hostname = await self.get_hostname()
        mac = await self.get_mac()

        if model:
            data.model = model

        if hostname:
            data.hostname = hostname

        if mac:
            data.mac = mac

        data.fault_light = await self.check_light()

        miner_data = None
        for i in range(PyasicSettings().miner_get_data_retries):
            miner_data = await self.api.multicommand(
                "summary", "pools", "stats", ignore_x19_error=True
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
                    hr = hr[0].get("GHS av")
                    if hr:
                        data.hashrate = round(hr / 1000, 2)

        if stats:
            boards = stats.get("STATS")
            if boards:
                if len(boards) > 0:
                    for board_num in range(1, 16, 5):
                        for _b_num in range(5):
                            b = boards[1].get(f"chain_acn{board_num + _b_num}")

                            if b and not b == 0 and board_offset == -1:
                                board_offset = board_num
                    if board_offset == -1:
                        board_offset = 1

                    data.left_chips = boards[1].get(f"chain_acn{board_offset}")
                    data.center_chips = boards[1].get(f"chain_acn{board_offset+1}")
                    data.right_chips = boards[1].get(f"chain_acn{board_offset+2}")

                    data.left_board_hashrate = round(
                        float(boards[1].get(f"chain_rate{board_offset}")) / 1000, 2
                    )
                    data.center_board_hashrate = round(
                        float(boards[1].get(f"chain_rate{board_offset+1}")) / 1000, 2
                    )
                    data.right_board_hashrate = round(
                        float(boards[1].get(f"chain_rate{board_offset+2}")) / 1000, 2
                    )

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

                    board_map = {0: "left_board", 1: "center_board", 2: "right_board"}
                    env_temp_list = []
                    for item in range(3):
                        board_temp = temp[1].get(f"temp{item + board_offset}")
                        chip_temp = temp[1].get(f"temp2_{item + board_offset}")
                        setattr(data, f"{board_map[item]}_chip_temp", chip_temp)
                        setattr(data, f"{board_map[item]}_temp", board_temp)
                        if f"temp_pcb{item}" in temp[1].keys():
                            env_temp = temp[1][f"temp_pcb{item}"].split("-")[0]
                            if not env_temp == 0:
                                env_temp_list.append(int(env_temp))
                    data.env_temp = sum(env_temp_list) / len(env_temp_list)

        if pools:
            pool_1 = None
            pool_2 = None
            pool_1_user = None
            pool_2_user = None
            pool_1_quota = 1
            pool_2_quota = 1
            quota = 0
            for pool in pools.get("POOLS"):
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
