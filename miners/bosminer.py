from miners import BaseMiner
from API.bosminer import BOSMinerAPI
import asyncssh
import toml
from config.bos import bos_config_convert, general_config_convert_bos


class BOSMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BOSMinerAPI(ip)
        super().__init__(ip, api)
        self.model = None
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
        """Sends command to turn on fault light on the miner."""
        await self.send_ssh_command('miner fault_light on')

    async def fault_light_off(self) -> None:
        """Sends command to turn off fault light on the miner."""
        await self.send_ssh_command('miner fault_light off')

    async def restart_backend(self):
        await self.restart_bosminer()

    async def restart_bosminer(self) -> None:
        """Restart bosminer hashing process."""
        await self.send_ssh_command('/etc/init.d/bosminer restart')

    async def reboot(self) -> None:
        """Reboots power to the physical miner."""
        await self.send_ssh_command('/sbin/reboot')

    async def get_config(self) -> None:
        async with (await self._get_ssh_connection()) as conn:
            async with conn.start_sftp_client() as sftp:
                async with sftp.open('/etc/bosminer.toml') as file:
                    toml_data = toml.loads(await file.read())
        cfg = await bos_config_convert(toml_data)
        self.config = cfg

    async def get_hostname(self) -> str:
        """Attempts to get hostname from miner."""
        try:
            async with (await self._get_ssh_connection()) as conn:
                data = await conn.run('cat /proc/sys/kernel/hostname')
            return data.stdout.strip()
        except Exception as e:
            print(self.ip, e)
            return "BOSMiner Unknown"

    async def get_model(self):
        if self.model:
            return self.model + " (BOS)"
        version_data = await self.api.devdetails()
        if version_data:
            if not version_data["DEVDETAILS"] == []:
                self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
                return self.model + " (BOS)"
        return None

    async def send_config(self, yaml_config) -> None:
        """Configures miner with yaml config."""
        toml_conf = await general_config_convert_bos(yaml_config)
        async with (await self._get_ssh_connection()) as conn:
            async with conn.start_sftp_client() as sftp:
                async with sftp.open('/etc/bosminer.toml', 'w+') as file:
                    await file.write(toml_conf)
            await conn.run("/etc/init.d/bosminer restart")

    async def get_board_info(self) -> dict:
        """Gets data on each board and chain in the miner."""
        devdetails = await self.api.devdetails()
        if not devdetails.get("DEVDETAILS"):
            print("devdetails error", devdetails)
            return {6: [], 7: [], 8: []}
        devs = devdetails['DEVDETAILS']
        boards = {}
        for board in devs:
            boards[board["ID"]] = []
            boards[board["ID"]].append({
                "chain": board["ID"],
                "chip_count": board['Chips'],
                "chip_status": "o" * board['Chips']
            })
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
        chains = devs['DEVDETAILS']
        for chain in chains:
            if chain['Chips'] == 0:
                bad += 1
        if not bad > 0:
            return str(self.ip)
