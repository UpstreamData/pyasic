from miners import BaseMiner
from API.bosminer import BOSMinerAPI
import asyncssh
import toml


class BOSminer(BaseMiner):
    def __init__(self, ip: str):
        api = BOSMinerAPI(ip)
        super().__init__(ip, api)
        self.config = {}

    def __repr__(self):
        return f"BOSminer: {str(self.ip)}"

    async def get_ssh_connection(self, username: str, password: str) -> asyncssh.connect:
        """Create a new asyncssh connection"""
        conn = await asyncssh.connect(str(self.ip), known_hosts=None, username=username, password=password,
                                      server_host_key_algs=['ssh-rsa'])
        # return created connection
        return conn

    async def send_ssh_command(self, cmd):
        result = None
        conn = await self.get_ssh_connection('root', 'admin')
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

    async def fault_light_on(self):
        await self.send_ssh_command('miner fault_light on')

    async def fault_light_off(self):
        await self.send_ssh_command('miner fault_light off')

    async def bosminer_restart(self):
        await self.send_ssh_command('/etc/init.d/bosminer restart')

    async def reboot(self):
        await self.send_ssh_command('/sbin/reboot')

    async def get_config(self):
        async with asyncssh.connect(str(self.ip), known_hosts=None, username='root', password='admin',
                                    server_host_key_algs=['ssh-rsa']) as conn:
            async with conn.start_sftp_client() as sftp:
                async with sftp.open('/etc/bosminer.toml') as file:
                    toml_data = toml.loads(await file.read())
        self.config = toml_data
        return toml_data
