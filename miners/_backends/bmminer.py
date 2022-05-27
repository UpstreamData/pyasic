import ipaddress
import logging


from API.bmminer import BMMinerAPI
from miners import BaseMiner

from data import MinerData

from settings import MINER_FACTORY_GET_VERSION_RETRIES as DATA_RETRIES


class BMMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BMMinerAPI(ip)
        self.api_type = "BMMiner"
        self.uname = "root"
        self.pwd = "admin"

    async def get_model(self) -> str or None:
        """Get miner model.

        :return: Miner model or None.
        """
        # check if model is cached
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        # get devdetails data
        version_data = await self.api.devdetails()

        # if we get data back, parse it for model
        if version_data:
            # handle Antminer BMMiner as a base
            self.model = version_data["DEVDETAILS"][0]["Model"].replace("Antminer ", "")
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model

        # if we don't get devdetails, log a failed attempt
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_hostname(self) -> str:
        """Get miner hostname.

        :return: The hostname of the miner as a string or "?"
        """
        if self.hostname:
            return self.hostname
        try:
            # open an ssh connection
            async with (await self._get_ssh_connection()) as conn:
                # if we get the connection, check hostname
                if conn is not None:
                    # get output of the hostname file
                    data = await conn.run("cat /proc/sys/kernel/hostname")
                    host = data.stdout.strip()

                    # return hostname data
                    logging.debug(f"Found hostname for {self.ip}: {host}")
                    self.hostname = host
                    return self.hostname
                else:
                    # return ? if we fail to get hostname with no ssh connection
                    logging.warning(f"Failed to get hostname for miner: {self}")
                    return "?"
        except Exception:
            # return ? if we fail to get hostname with an exception
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def send_ssh_command(self, cmd: str) -> str or None:
        """Send a command to the miner over ssh.

        :param cmd: The command to run.

        :return: Result of the command or None.
        """
        result = None

        # open an ssh connection
        async with (await self._get_ssh_connection()) as conn:
            # 3 retries
            for i in range(3):
                try:
                    # run the command and get the result
                    result = await conn.run(cmd)
                    result = result.stdout

                except Exception as e:
                    # if the command fails, log it
                    logging.warning(f"{self} command {cmd} error: {e}")

                    # on the 3rd retry, return None
                    if i == 3:
                        return
                    continue
        # return the result, either command output or None
        return result

    async def get_config(self) -> list or None:
        """Get the pool configuration of the miner.

        :return: Pool config data or None.
        """
        # get pool data
        pools = await self.api.pools()
        pool_data = []

        # ensure we got pool data
        if not pools:
            return

        # parse all the pools
        for pool in pools["POOLS"]:
            pool_data.append({"url": pool["URL"], "user": pool["User"], "pwd": "123"})
        return pool_data

    async def reboot(self) -> bool:
        logging.debug(f"{self}: Sending reboot command.")
        _ret = await self.send_ssh_command("reboot")
        logging.debug(f"{self}: Reboot command completed.")
        if isinstance(_ret, str):
            return True
        return False

    async def get_data(self) -> MinerData:
        data = MinerData(ip=str(self.ip), ideal_chips=self.nominal_chips * 3)

        offset = 1
        if self.model == "S9":
            offset = 6

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
            boards = stats.get("STATS")
            if boards:
                if len(boards) > 0:
                    data.left_chips = boards[1].get(f"chain_acn{offset}")
                    data.center_chips = boards[1].get(f"chain_acn{offset+1}")
                    data.right_chips = boards[1].get(f"chain_acn{offset+2}")

        if stats:
            temp = stats.get("STATS")
            if temp:
                if len(temp) > 1:
                    if self.model == "S9":
                        data.fan_1 = temp[1].get("fan5")
                        data.fan_2 = temp[1].get("fan6")
                    else:
                        data.fan_1 = temp[1].get("fan1")
                        data.fan_2 = temp[1].get("fan2")
                        data.fan_3 = temp[1].get("fan3")
                        data.fan_4 = temp[1].get("fan4")

                    board_map = {0: "left_board", 1: "center_board", 2: "right_board"}
                    for item in range(3):
                        board_temp = temp[1].get(f"temp{item + offset}")
                        chip_temp = temp[1].get(f"temp2_{item + offset}")
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
