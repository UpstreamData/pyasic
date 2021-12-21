from miners import BaseMiner
from API.cgminer import CGMinerAPI
import asyncssh


class CGMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = CGMinerAPI(ip)
        super().__init__(ip, api)
        self.config = None
        self.uname = 'root'
        self.pwd = 'admin'

    def __repr__(self) -> str:
        return f"CGMiner: {str(self.ip)}"

    async def get_hostname(self) -> str:
        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run('cat /proc/sys/kernel/hostname')
                    return data.stdout.strip()
                else:
                    return "CGMiner Unknown"
        except Exception:
            return "CGMiner Unknown"

    async def send_config(self, _):
        return None  # ignore for now

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
            print(str(self.ip) + " Connection refused.")
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
        # handle result
        self._result_handler(result)

    @staticmethod
    def _result_handler(result: asyncssh.process.SSHCompletedProcess) -> None:
        if result is not None:
            if len(result.stdout) > 0:
                print("ssh stdout: \n" + result.stdout)
            if len(result.stderr) > 0:
                print("ssh stderr: \n" + result.stderrr)
            if len(result.stdout) <= 0 and len(result.stderr) <= 0:
                print("ssh stdout stderr empty")
            # if result.stdout != "":
            #     print(result.stdout)
            #     if result.stderr != "":
            #         print("ERROR: " + result.stderr)
            # elif result.stderr != "":
            #     print("ERROR: " + result.stderr)
            # else:
            #     print(cmd)

    async def restart_cgminer(self) -> None:
        commands = ['cgminer-api restart',
                    '/usr/bin/cgminer-monitor >/dev/null 2>&1']
        commands = ';'.join(commands)
        await self.send_ssh_command(commands)

    async def reboot(self) -> None:
        commands = ['reboot']
        commands = ';'.join(commands)
        await self.send_ssh_command(commands)

    async def start_cgminer(self) -> None:
        commands = ['mkdir -p /etc/tmp/',
                    'echo \"*/3 * * * * /usr/bin/cgminer-monitor\" > /etc/tmp/root',
                    'crontab -u root /etc/tmp/root',
                    '/usr/bin/cgminer-monitor >/dev/null 2>&1']
        commands = ';'.join(commands)
        await self.send_ssh_command(commands)

    async def stop_cgminer(self) -> None:
        commands = ['mkdir -p /etc/tmp/',
                    'echo \"\" > /etc/tmp/root',
                    'crontab -u root /etc/tmp/root',
                    'killall cgminer']
        commands = ';'.join(commands)
        await self.send_ssh_command(commands)

    async def get_config(self) -> None:
        async with (await self._get_ssh_connection()) as conn:
            command = 'cat /etc/config/cgminer'
            result = await conn.run(command, check=True)
            self._result_handler(result)
            self.config = result.stdout
            print(str(self.config))
