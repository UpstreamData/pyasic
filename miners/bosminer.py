from miners import BaseMiner
from API.bosminer import BOSMinerAPI
import toml
from config.bos import bos_config_convert, general_config_convert_bos
import logging
from settings import MINER_FACTORY_GET_VERSION_RETRIES as DATA_RETRIES


class BOSMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BOSMinerAPI(ip)
        super().__init__(ip, api)
        self.model = None
        self.config = None
        self.version = None
        self.uname = "root"
        self.pwd = "admin"
        self.nominal_chips = 63

    def __repr__(self) -> str:
        return f"BOSminer: {str(self.ip)}"

    async def send_ssh_command(self, cmd: str) -> str or None:
        """Send a command to the miner over ssh.

        :return: Result of the command or None.
        """
        result = None

        # open an ssh connection
        async with (await self._get_ssh_connection()) as conn:
            # 3 retries
            for i in range(3):
                try:
                    # run the command and get the result
                    result = await conn.run(cmd)
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

    async def restart_backend(self) -> None:
        await self.restart_bosminer()

    async def restart_bosminer(self) -> None:
        """Restart bosminer hashing process."""
        logging.debug(f"{self}: Sending bosminer restart command.")
        await self.send_ssh_command("/etc/init.d/bosminer restart")
        logging.debug(f"{self}: bosminer restart command completed.")

    async def reboot(self) -> None:
        """Reboots power to the physical miner."""
        logging.debug(f"{self}: Sending reboot command.")
        await self.send_ssh_command("/sbin/reboot")
        logging.debug(f"{self}: Reboot command completed.")

    async def get_config(self) -> None:
        logging.debug(f"{self}: Getting config.")
        async with (await self._get_ssh_connection()) as conn:
            logging.debug(f"{self}: Opening SFTP connection.")
            async with conn.start_sftp_client() as sftp:
                logging.debug(f"{self}: Reading config file.")
                async with sftp.open("/etc/bosminer.toml") as file:
                    toml_data = toml.loads(await file.read())
        logging.debug(f"{self}: Converting config file.")
        cfg = bos_config_convert(toml_data)
        self.config = cfg

    async def get_hostname(self) -> str:
        """Get miner hostname.

        :return: The hostname of the miner as a string or "?"
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
        except Exception as e:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def get_model(self) -> str or None:
        """Get miner model.

        :return: Miner model or None.
        """
        # check if model is cached
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model} (BOS)")
            return self.model + " (BOS)"

        # get devdetails data
        version_data = await self.api.devdetails()

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

    async def get_version(self):
        """Get miner firmware version.

        :return: Miner firmware version or None.
        """
        # check if version is cached
        if self.version:
            logging.debug(f"Found version for {self.ip}: {self.version}")
            return self.version

        # get output of bos version file
        version_data = await self.send_ssh_command("cat /etc/bos_version")

        # if we get the version data, parse it
        if version_data:
            self.version = version_data.stdout.split("-")[5]
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
            toml_conf = toml.dumps(
                general_config_convert_bos(yaml_config, user_suffix=suffix)
            )
        else:
            toml_conf = toml.dumps(general_config_convert_bos(yaml_config))
        async with (await self._get_ssh_connection()) as conn:
            logging.debug(f"{self}: Opening SFTP connection.")
            async with conn.start_sftp_client() as sftp:
                logging.debug(f"{self}: Opening config file.")
                async with sftp.open("/etc/bosminer.toml", "w+") as file:
                    await file.write(toml_conf)
            logging.debug(f"{self}: Restarting BOSMiner")
            await conn.run("/etc/init.d/bosminer restart")

    async def get_board_info(self) -> dict:
        """Gets data on each board and chain in the miner."""
        logging.debug(f"{self}: Getting board info.")
        devdetails = await self.api.devdetails()
        if not devdetails.get("DEVDETAILS"):
            print("devdetails error", devdetails)
            return {0: [], 1: [], 2: []}
        devs = devdetails["DEVDETAILS"]
        boards = {}
        offset = devs[0]["ID"]
        for board in devs:
            boards[board["ID"] - offset] = []
            if not board["Chips"] == self.nominal_chips:
                nominal = False
            else:
                nominal = True
            boards[board["ID"] - offset].append(
                {
                    "chain": board["ID"] - offset,
                    "chip_count": board["Chips"],
                    "chip_status": "o" * board["Chips"],
                    "nominal": nominal,
                }
            )
        logging.debug(f"Found board data for {self}: {boards}")
        return boards

    async def get_bad_boards(self) -> dict:
        """Checks for and provides list of non working boards."""
        boards = await self.get_board_info()
        bad_boards = {}
        for board in boards.keys():
            for chain in boards[board]:
                if not chain["chip_count"] == 63:
                    if board not in bad_boards.keys():
                        bad_boards[board] = []
                    bad_boards[board].append(chain)
        return bad_boards

    async def check_good_boards(self) -> str:
        """Checks for and provides list for working boards."""
        devs = await self.api.devdetails()
        bad = 0
        chains = devs["DEVDETAILS"]
        for chain in chains:
            if chain["Chips"] == 0:
                bad += 1
        if not bad > 0:
            return str(self.ip)

    async def get_data(self):
        data = {
            "IP": str(self.ip),
            "Model": "Unknown",
            "Hostname": "Unknown",
            "Hashrate": 0,
            "Temperature": 0,
            "Pool User": "Unknown",
            "Wattage": 0,
            "Split": 0,
            "Pool 1": "Unknown",
            "Pool 1 User": "Unknown",
            "Pool 2": "",
            "Pool 2 User": "",
        }
        model = await self.get_model()
        hostname = await self.get_hostname()

        if model:
            data["Model"] = model

        if hostname:
            data["Hostname"] = hostname

        miner_data = None
        for i in range(DATA_RETRIES):
            miner_data = await self.api.multicommand(
                "summary", "temps", "tunerstatus", "pools"
            )
            if miner_data:
                break
        if not miner_data:
            return data
        summary = miner_data.get("summary")[0]
        temps = miner_data.get("temps")[0]
        tunerstatus = miner_data.get("tunerstatus")[0]
        pools = miner_data.get("pools")[0]

        if summary:
            hr = summary.get("SUMMARY")
            if hr:
                if len(hr) > 0:
                    hr = hr[0].get("MHS 5s")
                    if hr:
                        data["Hashrate"] = round(hr / 1000000, 2)

        if temps:
            temp = temps.get("TEMPS")
            if temp:
                if len(temp) > 0:
                    temp = temp[0].get("Chip")
                    if temp:
                        data["Temperature"] = round(temp)

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
                pool_1 = pool_1.replace("stratum+tcp://", "")
                pool_1 = pool_1.replace("stratum2+tcp://", "")
                data["Pool 1"] = pool_1

            if pool_1_user:
                data["Pool 1 User"] = pool_1_user
                data["Pool User"] = pool_1_user

            if pool_2:
                pool_2 = pool_2.replace("stratum+tcp://", "")
                pool_2 = pool_2.replace("stratum2+tcp://", "")
                data["Pool 2"] = pool_2

            if pool_2_user:
                data["Pool 2 User"] = pool_2_user

            if quota:
                data["Split"] = quota

        if tunerstatus:
            tuner = tunerstatus.get("TUNERSTATUS")
            if tuner:
                if len(tuner) > 0:
                    wattage = tuner[0].get("PowerLimit")
                    if wattage:
                        data["Wattage"] = wattage

        return data
