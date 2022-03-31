from miners import BaseMiner
from API.cgminer import CGMinerAPI
from API import APIError


class CGMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = CGMinerAPI(ip)
        super().__init__(ip, api)
        self.model = None
        self.config = None
        self.uname = "root"
        self.pwd = "admin"

    def __repr__(self) -> str:
        return f"CGMiner: {str(self.ip)}"

    async def get_model(self):
        if self.model:
            return self.model
        try:
            version_data = await self.api.devdetails()
        except APIError:
            return None
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
            return self.model
        return None

    async def get_hostname(self) -> str:
        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    return data.stdout.strip()
                else:
                    return "?"
        except Exception:
            return "?"

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

    async def restart_backend(self) -> None:
        await self.restart_cgminer()

    async def restart_cgminer(self) -> None:
        commands = ["cgminer-api restart", "/usr/bin/cgminer-monitor >/dev/null 2>&1"]
        commands = ";".join(commands)
        await self.send_ssh_command(commands)

    async def reboot(self) -> None:
        await self.send_ssh_command("reboot")

    async def start_cgminer(self) -> None:
        commands = [
            "mkdir -p /etc/tmp/",
            'echo "*/3 * * * * /usr/bin/cgminer-monitor" > /etc/tmp/root',
            "crontab -u root /etc/tmp/root",
            "/usr/bin/cgminer-monitor >/dev/null 2>&1",
        ]
        commands = ";".join(commands)
        await self.send_ssh_command(commands)

    async def stop_cgminer(self) -> None:
        commands = [
            "mkdir -p /etc/tmp/",
            'echo "" > /etc/tmp/root',
            "crontab -u root /etc/tmp/root",
            "killall cgminer",
        ]
        commands = ";".join(commands)
        await self.send_ssh_command(commands)

    async def get_config(self) -> None:
        async with (await self._get_ssh_connection()) as conn:
            command = "cat /etc/config/cgminer"
            result = await conn.run(command, check=True)
            self.config = result.stdout
            print(str(self.config))
