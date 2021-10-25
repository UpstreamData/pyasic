from miners import BaseMiner
from API.bosminer import BOSMinerAPI
import asyncssh
import toml
import time


class BOSminer(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BOSMinerAPI(ip)
        super().__init__(ip, api)
        self.config = None
        self.uname = 'root'
        self.pwd = 'admin'

    def __repr__(self) -> str:
        return f"BOSminer: {str(self.ip)}"

    async def _get_ssh_connection(self) -> asyncssh.connect:
        """Create a new asyncssh connection"""
        conn = await asyncssh.connect(str(self.ip), known_hosts=None, username=self.uname, password=self.pwd,
                                      server_host_key_algs=['ssh-rsa'])
        # return created connection
        return conn

    async def send_ssh_command(self, cmd: str) -> None:
        result = None
        async with self._get_ssh_connection() as conn:
            for i in range(3):
                try:
                    result = await conn.run(cmd)
                except Exception as e:
                    print(f"{cmd} error: {e}")
                    if i == 3:
                        return
                    continue
        # let the user know the result of the command
        if result is not None:
            if result.stdout != "":
                print(result.stdout)
                if result.stderr != "":
                    print("ERROR: " + result.stderr)
            elif result.stderr != "":
                print("ERROR: " + result.stderr)
            else:
                print(cmd)

    async def fault_light_on(self) -> None:
        await self.send_ssh_command('miner fault_light on')

    async def fault_light_off(self) -> None:
        await self.send_ssh_command('miner fault_light off')

    async def restart_backend(self) -> None:
        await self.send_ssh_command('/etc/init.d/bosminer restart')

    async def reboot(self) -> None:
        await self.send_ssh_command('/sbin/reboot')

    async def get_config(self) -> None:
        async with asyncssh.connect(str(self.ip), known_hosts=None, username='root', password='admin',
                                    server_host_key_algs=['ssh-rsa']) as conn:
            async with conn.start_sftp_client() as sftp:
                async with sftp.open('/etc/bosminer.toml') as file:
                    toml_data = toml.loads(await file.read())
        self.config = toml_data

    def update_config(self, config: dict) -> None:
        self.config = config

    async def get_hostname(self) -> str:
        async with asyncssh.connect(str(self.ip), known_hosts=None, username='root', password='admin',
                                    server_host_key_algs=['ssh-rsa']) as conn:
            data = await conn.run('cat /proc/sys/kernel/hostname')
        return data.stdout.strip()

    async def change_config_format(self, update_config: bool = False) -> dict:
        if not self.config:
            await self.get_config()
        config = self.config
        config['format']['generator'] = 'upstream_data_configurator'
        config['format']['timestamp'] = int(time.time())
        if update_config:
            self.update_config(config)
        return config

    async def change_config_tuning(self, wattage: int, enabled: bool = True, update_config: bool = False) -> dict:
        if not self.config:
            await self.get_config()
        config = self.config
        config['autotuning']['psu_power_limit'] = wattage
        config['autotuning']['enabled'] = enabled
        if update_config:
            self.update_config(config)
        return config

    async def change_config_temp_ctrl(self, target: float = 80.0, hot: float = 100.0,
                                      dangerous: float = 110.0, update_config: bool = False) -> dict:
        if not self.config:
            await self.get_config()
        config = self.config
        config['target_temp'] = target
        config['hot_temp'] = hot
        config['dangerous_temp'] = dangerous
        if update_config:
            self.update_config(config)
        return config

    async def send_config(self, config: dict) -> None:
        toml_conf = toml.dumps(config)
        async with asyncssh.connect(str(self.ip), known_hosts=None, username='root', password='admin',
                                    server_host_key_algs=['ssh-rsa']) as conn:
            async with conn.start_sftp_client() as sftp:
                async with sftp.open('/etc/bosminer.toml', 'w+') as file:
                    await file.write(toml_conf)
            await conn.run("/etc/init.d/bosminer restart")

    async def get_bad_boards(self) -> list:
        devs = await self.api.devdetails()
        bad = 0
        chains = devs['DEVDETAILS']
        for chain in chains:
            if chain['Chips'] == 0:
                bad += 1
        if bad > 0:
            return [str(self.ip), bad]

    async def check_good_boards(self) -> str:
        devs = await self.api.devdetails()
        bad = 0
        chains = devs['DEVDETAILS']
        for chain in chains:
            if chain['Chips'] == 0:
                bad += 1
        if not bad > 0:
            return str(self.ip)