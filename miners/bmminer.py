from API.bmminer import BMMinerAPI
from miners import BaseMiner
import logging


class BMMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BMMinerAPI(ip)
        super().__init__(ip, api)
        self.model = None
        self.config = None
        self.uname = 'root'
        self.pwd = 'admin'

    def __repr__(self) -> str:
        return f"BMMiner: {str(self.ip)}"

    async def get_model(self):
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model
        version_data = await self.api.devdetails()
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_hostname(self) -> str:
        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run('cat /proc/sys/kernel/hostname')
                    host = data.stdout.strip()
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    return host
                else:
                    logging.warning(f"Failed to get hostname for miner: {self}")
                    return "?"
        except Exception as e:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def send_ssh_command(self, cmd):
        result = None
        async with (await self._get_ssh_connection()) as conn:
            for i in range(3):
                try:
                    result = await conn.run(cmd)
                except Exception as e:
                    logging.warning(f"{self} command {cmd} error: {e}")
                    if i == 3:
                        return
                    continue
        return result

    async def reboot(self) -> None:
        logging.debug(f"{self}: Sending reboot command.")
        await self.send_ssh_command("reboot")
        logging.debug(f"{self}: Reboot command completed.")
