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


from pyasic.API.cgminer import CGMinerAPI
from pyasic.miners import BaseMiner
from pyasic.API import APIError

from pyasic.data import MinerData

from pyasic.settings import PyasicSettings


class CGMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = CGMinerAPI(ip)
        self.api_type = "CGMiner"
        self.uname = "root"
        self.pwd = "admin"
        self.config = None

    async def get_model(self) -> Union[str, None]:
        """Get miner model.

        Returns:
            Miner model or None.
        """
        if self.model:
            return self.model
        try:
            version_data = await self.api.devdetails()
        except APIError:
            return None
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
            return self.model
        return None

    async def get_hostname(self) -> Union[str, None]:
        """Get miner hostname.

        Returns:
            The hostname of the miner as a string or "?"
        """
        if self.hostname:
            return self.hostname
        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()
                    self.hostname = host
                    return self.hostname
                else:
                    return None
        except Exception:
            return None

    async def send_ssh_command(self, cmd: str) -> Union[str, None]:
        """Send a command to the miner over ssh.

        Parameters:
            cmd: The command to run.

        Returns:
            Result of the command or None.
        """
        result = None
        async with (await self._get_ssh_connection()) as conn:
            for i in range(3):
                try:
                    result = await conn.run(cmd)
                    result = result.stdout
                except Exception as e:
                    print(f"{cmd} error: {e}")
                    if i == 3:
                        return
                    continue
        return result

    async def restart_backend(self) -> bool:
        """Restart cgminer hashing process.  Wraps [`restart_cgminer`][pyasic.miners._backends.cgminer.CGMiner.restart_cgminer] to standardize."""
        return await self.restart_cgminer()

    async def restart_cgminer(self) -> bool:
        """Restart cgminer hashing process."""
        commands = ["cgminer-api restart", "/usr/bin/cgminer-monitor >/dev/null 2>&1"]
        commands = ";".join(commands)
        _ret = await self.send_ssh_command(commands)
        if isinstance(_ret, str):
            return True
        return False

    async def reboot(self) -> bool:
        """Reboots power to the physical miner."""
        logging.debug(f"{self}: Sending reboot command.")
        _ret = await self.send_ssh_command("reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def start_cgminer(self) -> None:
        """Start cgminer hashing process."""
        commands = [
            "mkdir -p /etc/tmp/",
            'echo "*/3 * * * * /usr/bin/cgminer-monitor" > /etc/tmp/root',
            "crontab -u root /etc/tmp/root",
            "/usr/bin/cgminer-monitor >/dev/null 2>&1",
        ]
        commands = ";".join(commands)
        await self.send_ssh_command(commands)

    async def stop_cgminer(self) -> None:
        """Restart cgminer hashing process."""
        commands = [
            "mkdir -p /etc/tmp/",
            'echo "" > /etc/tmp/root',
            "crontab -u root /etc/tmp/root",
            "killall cgminer",
        ]
        commands = ";".join(commands)
        await self.send_ssh_command(commands)

    async def get_config(self) -> str:
        """Gets the config for the miner and sets it as `self.config`.

        Returns:
            The config from `self.config`.
        """
        async with (await self._get_ssh_connection()) as conn:
            command = "cat /etc/config/cgminer"
            result = await conn.run(command, check=True)
            self.config = result.stdout
        return self.config

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
                    if pool.get("Quota"):
                        pool_2_quota = pool.get("Quota")
                elif not pool_2_user:
                    pool_2_user = pool.get("User")
                    pool_2 = pool["URL"]
                    if pool.get("Quota"):
                        pool_2_quota = pool.get("Quota")
                if not pool.get("User") == pool_1_user:
                    if not pool_2_user == pool.get("User"):
                        pool_2_user = pool.get("User")
                        pool_2 = pool["URL"]
                        if pool.get("Quota"):
                            pool_2_quota = pool.get("Quota")
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
