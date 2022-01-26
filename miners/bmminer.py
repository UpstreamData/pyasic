from API.bmminer import BMMinerAPI
from miners import BaseMiner
import asyncssh


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
            return self.model
        version_data = await self.api.devdetails()
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
            return self.model
        return None

    async def get_hostname(self) -> str:
        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run('cat /proc/sys/kernel/hostname')
                    return data.stdout.strip()
                else:
                    return "?"
        except Exception:
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
                print(e)
        except OSError:
            print(str(self.ip) + ": Connection refused.")
            return None

    async def send_ssh_command(self, cmd):
        result = None
        async with (await self._get_ssh_connection()) as conn:
            for i in range(3):
                try:
                    result = await conn.run(cmd)
                except Exception as e:
                    print(f"{cmd} error: {e}")
                    if i == 3:
                        return
                    continue
        return result

    async def reboot(self) -> None:
        await self.send_ssh_command("reboot")
