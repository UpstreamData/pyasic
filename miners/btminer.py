from API.btminer import BTMinerAPI
from miners import BaseMiner
from API import APIError


class BTMiner(BaseMiner):
    def __init__(self, ip: str) -> None:
        api = BTMinerAPI(ip)
        self.model = None
        super().__init__(ip, api)
        self.nominal_chips = 66

    def __repr__(self) -> str:
        return f"BTMiner: {str(self.ip)}"

    async def get_model(self):
        if self.model:
            return self.model
        version_data = await self.api.devdetails()
        if version_data:
            self.model = version_data["DEVDETAILS"][0]["Model"].split("V")[0]
            return self.model
        return None

    async def get_hostname(self) -> str:
        try:
            host_data = await self.api.get_miner_info()
            if host_data:
                return host_data["Msg"]["hostname"]
        except APIError:
            return "?"


    async def get_board_info(self) -> dict:
        """Gets data on each board and chain in the miner."""
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
                if not board['Effective Chips'] in self.nominal_chips:
                    nominal = False
                else:
                    nominal = True
                boards[board["ID"] - offset].append({
                    "chain": board["ID"] - offset,
                    "chip_count": board['Effective Chips'],
                    "chip_status": "o" * board['Effective Chips'],
                    "nominal": nominal
                })
            else:
                print(board)
        return boards

