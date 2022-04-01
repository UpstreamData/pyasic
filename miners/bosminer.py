from miners import BaseMiner
from API.bosminer import BOSMinerAPI
import toml
from config.bos import bos_config_convert, general_config_convert_bos
import logging


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

    async def send_ssh_command(self, cmd: str):
        """Sends SSH command to miner."""
        # creates result variable
        result = None

        # runs the command on the miner
        async with (await self._get_ssh_connection()) as conn:
            # attempt to run command up to 3 times
            for i in range(3):
                try:
                    # save result of the command
                    result = await conn.run(cmd)
                except Exception as e:
                    logging.warning(f"{self} command {cmd} error: {e}")
                    if i == 3:
                        return
                    continue
        return result

    async def fault_light_on(self) -> None:
        """Sends command to turn on fault light on the miner."""
        logging.debug(f"{self}: Sending fault_light on command.")
        await self.send_ssh_command("miner fault_light on")
        logging.debug(f"{self}: fault_light on command completed.")

    async def fault_light_off(self) -> None:
        """Sends command to turn off fault light on the miner."""
        logging.debug(f"{self}: Sending fault_light off command.")
        await self.send_ssh_command("miner fault_light off")
        logging.debug(f"{self}: fault_light off command completed.")

    async def restart_backend(self):
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
        cfg = await bos_config_convert(toml_data)
        self.config = cfg

    async def get_hostname(self) -> str:
        """Attempts to get hostname from miner."""
        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    return host
                else:
                    logging.warning(f"Failed to get hostname for miner: {self}")
                    return "?"
        except Exception as e:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def get_model(self):
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model} (BOS)")
            return self.model + " (BOS)"
        version_data = await self.api.devdetails()
        if version_data:
            if not version_data["DEVDETAILS"] == []:
                self.model = version_data["DEVDETAILS"][0]["Model"].replace(
                    "Antminer ", ""
                )
                logging.debug(f"Found model for {self.ip}: {self.model} (BOS)")
                return self.model + " (BOS)"
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_version(self):
        if self.version:
            logging.debug(f"Found version for {self.ip}: {self.version}")
            return self.version
        version_data = await self.send_ssh_command("cat /etc/bos_version")
        if version_data:
            self.version = version_data.stdout.split("-")[5]
            logging.debug(f"Found version for {self.ip}: {self.version}")
            return self.version
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def send_config(self, yaml_config) -> None:
        """Configures miner with yaml config."""
        logging.debug(f"{self}: Sending config.")
        toml_conf = toml.dumps(await general_config_convert_bos(yaml_config))
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
