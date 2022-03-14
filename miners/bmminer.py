from API.bmminer import BMMinerAPI
from miners import BaseMiner
import asyncssh
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
        except Exception:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def _get_ssh_connection(self) -> asyncssh.connect:
        try:
            conn = await asyncssh.connect(str(self.ip),
                                          known_hosts=None,
                                          username=self.uname,
                                          password=self.pwd,
                                          server_host_key_algs=['ssh-rsa'])
            return conn
        except asyncssh.misc.PermissionDenied:
            try:
                conn = await asyncssh.connect(str(self.ip),
                                              known_hosts=None,
                                              username="admin",
                                              password="admin",
                                              server_host_key_algs=['ssh-rsa'])
                return conn
            except Exception as e:
                logging.warning(f"{self} raised an exception: {e}")
                raise e
        except OSError:
            logging.warning(f"Connection refused: {self} ")
            return None
        except Exception as e:
            logging.warning(f"{self} raised an exception: {e}")
            raise e

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
