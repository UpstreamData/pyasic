from miners import BaseMiner
from API.bosminer import BOSMinerAPI
import toml
from config.bos import bos_config_convert, general_config_convert_bos
import logging
from settings import MINER_FACTORY_GET_VERSION_RETRIES as DATA_RETRIES
import asyncssh


class BOSMinerOld(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.api = BOSMinerAPI(ip)
        self.api_type = "BOSMiner"
        self.uname = "root"
        self.pwd = "admin"

    async def send_ssh_command(self, cmd: str) -> str or None:
        """Send a command to the miner over ssh.

        :return: Result of the command or None.
        """
        result = None

        # open an ssh connection
        async with await asyncssh.connect("192.168.1.11", username="root") as conn:
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

    async def update_to_plus(self):
        result = await self.send_ssh_command("opkg update && opkg install bos_plus")
        return result
