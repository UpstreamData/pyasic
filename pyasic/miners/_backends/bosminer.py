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
import json
from typing import Union

import toml


from pyasic.miners import BaseMiner
from pyasic.API.bosminer import BOSMinerAPI
from pyasic.API import APIError

from pyasic.data.error_codes import BraiinsOSError
from pyasic.data import MinerData

from pyasic.config import MinerConfig

from pyasic.settings import PyasicSettings


class BOSMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BOSMinerAPI(ip)
        self.api_type = "BOSMiner"
        self.uname = "root"
        self.pwd = "admin"
        self.config = None

    async def send_ssh_command(self, cmd: str) -> Union[str, None]:
        """Send a command to the miner over ssh.

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
        return str(result)

    async def fault_light_on(self) -> bool:
        """Sends command to turn on fault light on the miner."""
        logging.debug(f"{self}: Sending fault_light on command.")
        self.light = True
        _ret = await self.send_ssh_command("miner fault_light on")
        logging.debug(f"{self}: fault_light on command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def fault_light_off(self) -> bool:
        """Sends command to turn off fault light on the miner."""
        logging.debug(f"{self}: Sending fault_light off command.")
        self.light = False
        _ret = await self.send_ssh_command("miner fault_light off")
        logging.debug(f"{self}: fault_light off command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def restart_backend(self) -> bool:
        """Restart bosminer hashing process.  Wraps [`restart_bosminer`][pyasic.miners._backends.bosminer.BOSMiner.restart_bosminer] to standardize."""
        return await self.restart_bosminer()

    async def restart_bosminer(self) -> bool:
        """Restart bosminer hashing process."""
        logging.debug(f"{self}: Sending bosminer restart command.")
        _ret = await self.send_ssh_command("/etc/init.d/bosminer restart")
        logging.debug(f"{self}: bosminer restart command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def reboot(self) -> bool:
        """Reboots power to the physical miner."""
        logging.debug(f"{self}: Sending reboot command.")
        _ret = await self.send_ssh_command("/sbin/reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def get_config(self) -> MinerConfig:
        """Gets the config for the miner and sets it as `self.config`.

        Returns:
            The config from `self.config`.
        """
        logging.debug(f"{self}: Getting config.")
        async with (await self._get_ssh_connection()) as conn:
            logging.debug(f"{self}: Opening SFTP connection.")
            async with conn.start_sftp_client() as sftp:
                logging.debug(f"{self}: Reading config file.")
                async with sftp.open("/etc/bosminer.toml") as file:
                    toml_data = toml.loads(await file.read())
        logging.debug(f"{self}: Converting config file.")
        cfg = MinerConfig().from_raw(toml_data)
        self.config = cfg
        return self.config

    async def get_hostname(self) -> str:
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
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    self.hostname = host
                    return self.hostname
                else:
                    logging.warning(f"Failed to get hostname for miner: {self}")
                    return "?"
        except Exception:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def get_model(self) -> Union[str, None]:
        """Get miner model.

        Returns:
            Miner model or None.
        """
        # check if model is cached
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model} (BOS)")
            return self.model + " (BOS)"

        # get devdetails data
        try:
            version_data = await self.api.devdetails()
        except APIError as e:
            version_data = None
            if e.message == "Not ready":
                cfg = json.loads(await self.send_ssh_command("bosminer config --data"))
                model = cfg.get("data").get("format").get("model")
                if model:
                    model = model.replace("Antminer ", "")
                    self.model = model
                    return self.model + " (BOS)"

        # if we get data back, parse it for model
        if version_data:
            if not version_data["DEVDETAILS"] == []:
                # handle Antminer BOSMiner as a base
                self.model = version_data["DEVDETAILS"][0]["Model"].replace(
                    "Antminer ", ""
                )
                logging.debug(f"Found model for {self.ip}: {self.model} (BOS)")
                return self.model + " (BOS)"

        # if we don't get devdetails, log a failed attempt
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_version(self) -> Union[str, None]:
        """Get miner firmware version.

        Returns:
            Miner firmware version or None.
        """
        # check if version is cached
        if self.version:
            logging.debug(f"Found version for {self.ip}: {self.version}")
            return self.version

        # get output of bos version file
        version_data = await self.send_ssh_command("cat /etc/bos_version")

        # if we get the version data, parse it
        if version_data:
            self.version = version_data.split("-")[5]
            logging.debug(f"Found version for {self.ip}: {self.version}")
            return self.version

        # if we fail to get version, log a failed attempt
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def send_config(self, yaml_config, ip_user: bool = False) -> None:
        """Configures miner with yaml config."""
        logging.debug(f"{self}: Sending config.")
        if ip_user:
            suffix = str(self.ip).split(".")[-1]
            toml_conf = (
                MinerConfig()
                .from_yaml(yaml_config)
                .as_bos(model=self.model.replace(" (BOS)", ""), user_suffix=suffix)
            )
        else:
            toml_conf = (
                MinerConfig()
                .from_yaml(yaml_config)
                .as_bos(model=self.model.replace(" (BOS)", ""))
            )
        async with (await self._get_ssh_connection()) as conn:
            await conn.run("/etc/init.d/bosminer stop")
            logging.debug(f"{self}: Opening SFTP connection.")
            async with conn.start_sftp_client() as sftp:
                logging.debug(f"{self}: Opening config file.")
                async with sftp.open("/etc/bosminer.toml", "w+") as file:
                    await file.write(toml_conf)
            logging.debug(f"{self}: Restarting BOSMiner")
            await conn.run("/etc/init.d/bosminer start")

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
            try:
                miner_data = await self.api.multicommand(
                    "summary",
                    "temps",
                    "tunerstatus",
                    "pools",
                    "devdetails",
                    "fans",
                    "devs",
                )
            except APIError as e:
                if str(e.message) == "Not ready":
                    miner_data = await self.api.multicommand(
                        "summary", "tunerstatus", "pools", "devs"
                    )
            if miner_data:
                break
        if not miner_data:
            return data
        summary = miner_data.get("summary")
        temps = miner_data.get("temps")
        tunerstatus = miner_data.get("tunerstatus")
        pools = miner_data.get("pools")
        devdetails = miner_data.get("devdetails")
        devs = miner_data.get("devs")
        fans = miner_data.get("fans")

        if summary:
            hr = summary[0].get("SUMMARY")
            if hr:
                if len(hr) > 0:
                    hr = hr[0].get("MHS 1m")
                    if hr:
                        data.hashrate = round(hr / 1000000, 2)

        if temps:
            temp = temps[0].get("TEMPS")
            if temp:
                if len(temp) > 0:
                    board_map = {0: "left_board", 1: "center_board", 2: "right_board"}
                    offset = 6 if temp[0]["ID"] in [6, 7, 8] else temp[0]["ID"]
                    for board in temp:
                        _id = board["ID"] - offset
                        chip_temp = round(board["Chip"])
                        board_temp = round(board["Board"])
                        setattr(data, f"{board_map[_id]}_chip_temp", chip_temp)
                        setattr(data, f"{board_map[_id]}_temp", board_temp)

        if fans:
            fan_data = fans[0].get("FANS")
            if fan_data:
                for fan in range(self.fan_count):
                    setattr(data, f"fan_{fan+1}", fan_data[fan]["RPM"])

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

        if tunerstatus:
            tuner = tunerstatus[0].get("TUNERSTATUS")
            if tuner:
                if len(tuner) > 0:
                    wattage = tuner[0].get("ApproximateMinerPowerConsumption")
                    wattage_limit = tuner[0].get("PowerLimit")
                    if wattage_limit:
                        data.wattage_limit = wattage_limit
                    if wattage:
                        data.wattage = wattage

                    chain_status = tuner[0].get("TunerChainStatus")
                    if chain_status and len(chain_status) > 0:
                        board_map = {
                            0: "Left board",
                            1: "Center board",
                            2: "Right board",
                        }
                        offset = (
                            6
                            if chain_status[0]["HashchainIndex"] in [6, 7, 8]
                            else chain_status[0]["HashchainIndex"]
                        )
                        for board in chain_status:
                            _id = board["HashchainIndex"] - offset
                            if board["Status"] not in [
                                "Stable",
                                "Testing performance profile",
                            ]:
                                _error = board["Status"]
                                _error = _error[0].lower() + _error[1:]
                                data.errors.append(
                                    BraiinsOSError(f"{board_map[_id]} {_error}")
                                )

        if devdetails:
            boards = devdetails[0].get("DEVDETAILS")
            if boards:
                if len(boards) > 0:
                    board_map = {0: "left_chips", 1: "center_chips", 2: "right_chips"}
                    offset = 6 if boards[0]["ID"] in [6, 7, 8] else boards[0]["ID"]
                    for board in boards:
                        _id = board["ID"] - offset
                        chips = board["Chips"]
                        setattr(data, board_map[_id], chips)

        if devs:
            boards = devs[0].get("DEVS")
            if boards:
                if len(boards) > 0:
                    board_map = {
                        0: "left_board_hashrate",
                        1: "center_board_hashrate",
                        2: "right_board_hashrate",
                    }
                    offset = 6 if boards[0]["ID"] in [6, 7, 8] else boards[0]["ID"]
                    for board in boards:
                        _id = board["ID"] - offset
                        hashrate = round(board["MHS 1m"] / 1000000, 2)
                        setattr(data, board_map[_id], hashrate)
        return data

    async def get_mac(self):
        result = await self.send_ssh_command("cat /sys/class/net/eth0/address")
        return result.upper().strip()
