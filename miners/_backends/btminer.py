import ipaddress
import logging


from API.btminer import BTMinerAPI
from miners import BaseMiner
from API import APIError

from data import MinerData

from settings import MINER_FACTORY_GET_VERSION_RETRIES as DATA_RETRIES


class BTMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.ip = ipaddress.ip_address(ip)
        self.api = BTMinerAPI(ip)
        self.api_type = "BTMiner"

    async def get_model(self):
        if self.model:
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model
        version_data = await self.api.devdetails()
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].split("V")[0]
            logging.debug(f"Found model for {self.ip}: {self.model}")
            return self.model
        logging.warning(f"Failed to get model for miner: {self}")
        return None

    async def get_hostname(self) -> str:
        if self.hostname:
            return self.hostname
        try:
            host_data = await self.api.get_miner_info()
            if host_data:
                host = host_data["Msg"]["hostname"]
                logging.debug(f"Found hostname for {self.ip}: {host}")
                self.hostname = host
                return self.hostname
        except APIError:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"
        except Exception as e:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"

    async def get_board_info(self) -> dict:
        """Gets data on each board and chain in the miner."""
        logging.debug(f"{self}: Getting board info.")
        devs = await self.api.devs()
        if not devs.get("DEVS"):
            print("devs error", devs)
            return {0: [], 1: [], 2: []}
        devs = devs["DEVS"]
        boards = {}
        offset = devs[0]["ID"]
        for board in devs:
            boards[board["ID"] - offset] = []
            if "Effective Chips" in board.keys():
                if not board["Effective Chips"] in self.nominal_chips:
                    nominal = False
                else:
                    nominal = True
                boards[board["ID"] - offset].append(
                    {
                        "chain": board["ID"] - offset,
                        "chip_count": board["Effective Chips"],
                        "chip_status": "o" * board["Effective Chips"],
                        "nominal": nominal,
                    }
                )
            else:
                logging.warning(f"Incorrect board data from {self}: {board}")
                print(board)
        logging.debug(f"Found board data for {self}: {boards}")
        return boards

    async def get_mac(self):
        mac = ""
        data = await self.api.get_miner_info()
        if data:
            if "Msg" in data.keys():
                if "mac" in data["Msg"].keys():
                    mac = data["Msg"]["mac"]
        return str(mac).upper()

    async def get_data(self):
        data = MinerData(ip=str(self.ip), ideal_chips=self.nominal_chips * 3)

        try:
            model = await self.get_model()
            hostname = await self.get_hostname()
        except APIError:
            logging.warning(f"Failed to get hostname and model: {self}")
            model = None
            data.model = "Whatsminer"
            hostname = None
            data.hostname = "Whatsminer"

        if model:
            data.model = model

        if hostname:
            data.hostname = hostname
        miner_data = None
        for i in range(DATA_RETRIES):
            try:
                miner_data = await self.api.multicommand("summary", "devs", "pools")
                if miner_data:
                    break
            except APIError:
                pass

        if not miner_data:
            return data

        summary = miner_data.get("summary")[0]
        devs = miner_data.get("devs")[0]
        pools = miner_data.get("pools")[0]

        if summary:
            summary_data = summary.get("SUMMARY")
            if summary_data:
                if len(summary_data) > 0:
                    hr = summary_data[0].get("MHS 1m")
                    if hr:
                        data.hashrate = round(hr / 1000000, 2)

                    wattage = summary_data[0].get("Power")
                    if wattage:
                        data.wattage = round(wattage)

        if devs:
            temp_data = devs.get("DEVS")
            if temp_data:
                data.fan_1 = temp_data[0]["Fan Speed In"]
                data.fan_2 = temp_data[0]["Fan Speed Out"]

                board_map = {0: "left_board", 1: "center_board", 2: "right_board"}
                for board in temp_data:
                    id = board["ID"]
                    chip_temp = round(board["Chip Temp Avg"])
                    board_temp = round(board["Temperature"])
                    setattr(data, f"{board_map[id]}_chip_temp", chip_temp)
                    setattr(data, f"{board_map[id]}_temp", board_temp)

        if devs:
            boards = devs.get("DEVS")
            if boards:
                if len(boards) > 0:
                    board_map = {0: "left_chips", 1: "center_chips", 2: "right_chips"}
                    if "ID" in boards[0].keys():
                        id_key = "ID"
                    else:
                        id_key = "ASC"
                    offset = boards[0][id_key]
                    for board in boards:
                        id = board[id_key] - offset
                        chips = board["Effective Chips"]
                        setattr(data, board_map[id], chips)

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
