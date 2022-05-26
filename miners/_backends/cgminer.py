import ipaddress
import logging


from API.cgminer import CGMinerAPI
from miners import BaseMiner
from API import APIError

from data import MinerData

from settings import MINER_FACTORY_GET_VERSION_RETRIES as DATA_RETRIES


class CGMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = CGMinerAPI(ip)
        self.api_type = "CGMiner"
        self.uname = "root"
        self.pwd = "admin"

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
                    result = result.stdout
                except Exception as e:
                    print(f"{cmd} error: {e}")
                    if i == 3:
                        return
                    continue
        return result

    async def restart_backend(self) -> bool:
        return await self.restart_cgminer()

    async def restart_cgminer(self) -> bool:
        commands = ["cgminer-api restart", "/usr/bin/cgminer-monitor >/dev/null 2>&1"]
        commands = ";".join(commands)
        _ret = await self.send_ssh_command(commands)
        if isinstance(_ret, str):
            return True
        return False

    async def reboot(self) -> bool:
        logging.debug(f"{self}: Sending reboot command.")
        _ret = await self.send_ssh_command("reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(_ret, str):
            return True
        return False

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
        data = MinerData(ip=str(self.ip), ideal_chips=self.nominal_chips * 3)

        model = await self.get_model()
        hostname = await self.get_hostname()

        if model:
            data.model = model

        if hostname:
            data.hostname = hostname
        miner_data = None
        for i in range(DATA_RETRIES):
            miner_data = await self.api.multicommand("summary", "pools", "stats")
            if miner_data:
                break

        if not miner_data:
            return data

        summary = miner_data.get("summary")[0]
        pools = miner_data.get("pools")[0]
        stats = miner_data.get("stats")[0]

        if summary:
            hr = summary.get("SUMMARY")
            if hr:
                if len(hr) > 0:
                    hr = hr[0].get("GHS av")
                    if hr:
                        data.hashrate = round(hr / 1000, 2)

        if stats:
            temp = stats.get("STATS")
            if temp:
                if len(temp) > 1:
                    data.fan_1 = temp[1].get("fan1")
                    data.fan_2 = temp[1].get("fan2")
                    data.fan_3 = temp[1].get("fan3")
                    data.fan_4 = temp[1].get("fan4")

                    board_map = {1: "left_board", 2: "center_board", 3: "right_board"}
                    for item in range(1, 4):
                        board_temp = temp[1].get(f"temp{item}")
                        chip_temp = temp[1].get(f"temp2_{item}")
                        setattr(data, f"{board_map[item]}_chip_temp", chip_temp)
                        setattr(data, f"{board_map[item]}_temp", board_temp)

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
                pool_1 = pool_1.replace("stratum+tcp://", "").replace(
                    "stratum2+tcp://", ""
                )
                data.pool_1_url = pool_1

            if pool_1_user:
                data.pool_1_user = pool_1_user

            if pool_2:
                pool_2 = pool_2.replace("stratum+tcp://", "").replace(
                    "stratum2+tcp://", ""
                )
                data.pool_2_url = pool_2

            if pool_2_user:
                data.pool_2_user = pool_2_user

            if quota:
                data.pool_split = str(quota)

        return data
