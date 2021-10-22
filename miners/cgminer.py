from miners import BaseMiner
from API.cgminer import CGMinerAPI
import asyncssh


class CGMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = CGMinerAPI(ip)
        super().__init__(ip, api)
        self.config = None
        self.uname = 'root'
        self.pwd = 'root'

    def __repr__(self) -> str:
        return f"CGMiner: {str(self.ip)}"

    async def send_config(self):
        return None # ignore for now

    async def get_ssh_connection(self) -> asyncssh.connect:
        conn = await asyncssh.connect(str(self.ip),
                                      known_hosts=None,
                                      username=self.uname,
                                      password=self.pwd,
                                      server_host_key_algs=['ssh-rsa'])
        return conn

    async def result_handler(self, result: asyncssh.process.SSHCompletedProcess) -> None:
        if result is not None:
            if len(result.stdout) > 0:
                print("ssh stdout: \n" + result.stdout)
            if len(result.stderr) > 0:
                print("ssh stderr: \n" + result.stderrr)
            if len(result.stdout) <= 0 and len(result.stderr) <= 0:
                print("ssh stdout stderr empty")
        return None

    async def restart_cgminer(self) -> None:
        async with get_ssh_connection() as conn:
            commands = ['cgminer-api restart',
                        '/usr/bin/cgminer-monitor >/dev/null 2>&1']
            commands = ';'.join(commands)
            result = await conn.run(commands, check=True)
            result_handler(result)
        return None

    async def reboot(self) -> None:
        async with get_ssh_connection() conn:
            commands = ['reboot']
            commands = ';'.join(commands)
            result = await conn.run(commands, check=True)
            result_handler(result)
        return None

    async def start_cgminer(self) -> None:
        async with get_ssh_connection() conn:
            commands = ['mkdir -p /etc/tmp/',
                        'echo \"*/3 * * * * /usr/bin/cgminer-monitor\" > /etc/tmp/root',
                        'crontab -u root /etc/tmp/root',
                        '/usr/bin/cgminer-monitor >/dev/null 2>&1']
            commands = ';'.join(commands)
            result = await conn.run(commands, check=True)
            result_handler(result)
        return None

    async def stop_cgminer(self) -> None:
        async with get_ssh_connection() conn:
            commands = ['mkdir -p /etc/tmp/',
                        'echo \"\" > /etc/tmp/root',
                        'crontab -u root /etc/tmp/root',
                        'killall cgminer']
            commands = ';'.join(commands)
            result = await conn.run(commands, check=True)
            result_handler(result)
        return None

    async def get_config(self) -> None:
        async with get_ssh_connection() as conn:
            commands = ['cat /etc/config/cgminer']
            commands = ';'.join(commands)
            result = await conn.run(commands, check=True)
            result_handler(result)
            self.config = result.stdout
        return None