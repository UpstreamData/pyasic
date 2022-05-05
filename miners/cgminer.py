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
        if self.hostname:
            return self.hostname
        try:
            async with (await self._get_ssh_connection()) as conn:
                if conn is not None:
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()
                    self.hostname = host
                    return self.hostname
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

    async def get_data(self):
        data = {
            "IP": str(self.ip),
            "Model": "Unknown",
            "Hostname": "Unknown",
            "Hashrate": 0,
            "Temperature": 0,
            "Pool User": "Unknown",
            "Wattage": 0,
            "Split": 0,
            "Pool 1": "Unknown",
            "Pool 1 User": "Unknown",
            "Pool 2": "",
            "Pool 2 User": "",
        }

        miner_data = await self.api.multicommand("summary", "pools", "stats")
        model = await self.get_model()
        hostname = await self.get_hostname()

        summary = miner_data.get("summary")[0]
        pools = miner_data.get("pools")[0]
        stats = miner_data.get("stats")[0]

        if model:
            data["Model"] = model

        if hostname:
            data["Hostname"] = hostname

        if summary:
            hr = summary.get("SUMMARY")
            if hr:
                if len(hr) > 0:
                    hr = hr[0].get("GHS av")
                    if hr:
                        data["Hashrate"] = round(hr / 1000, 2)

        if stats:
            temp = stats.get("STATS")
            if temp:
                if len(temp) > 1:
                    for item in ["temp2", "temp1", "temp3"]:
                        temperature = temp[1].get(item)
                        if temperature and not temperature == 0.0:
                            data["Temperature"] = temperature

        if pools:
            pool_1 = None
            pool_2 = None
            pool_1_user = None
            pool_2_user = None
            pool_1_quota = 1
            pool_2_quota = 1
            quota = 0
            for pool in pools.get("POOLS"):
                if not pool_1_user:
                    pool_1_user = pool.get("User")
                    pool_1 = pool["URL"]
                    pool_1_quota = pool["Quota"]
                elif not pool_2_user:
                    pool_2_user = pool.get("User")
                    pool_2 = pool["URL"]
                    pool_2_quota = pool["Quota"]
                if not pool.get("User") == pool_1_user:
                    if not pool_2_user == pool.get("User"):
                        pool_2_user = pool.get("User")
                        pool_2 = pool["URL"]
                        pool_2_quota = pool["Quota"]
            if pool_2_user and not pool_2_user == pool_1_user:
                quota = f"{pool_1_quota}/{pool_2_quota}"

            if pool_1:
                data["Pool 1"] = pool_1

            if pool_1_user:
                data["Pool 1 User"] = pool_1_user
                data["Pool User"] = pool_1_user

            if pool_2:
                data["Pool 2"] = pool_2

            if pool_2_user:
                data["Pool 2 User"] = pool_2_user

            if quota:
                data["Split"] = quota
