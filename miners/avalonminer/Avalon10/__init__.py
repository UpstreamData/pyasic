from miners.cgminer import CGMiner
import logging


class CGMinerAvalon10(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "Avalon 10"
        self.api_type = "CGMiner"
        self.nominal_chips = 114

    async def get_hostname(self):
        try:
            devdetails = await self.api.devdetails()
            if devdetails:
                if len(devdetails.get("DEVDETAILS")) > 0:
                    if "Name" in devdetails["DEVDETAILS"][0]:
                        host = devdetails["DEVDETAILS"][0]["Name"]
                        logging.debug(f"Found hostname for {self.ip}: {host}")
                        return host
        except Exception as e:
            logging.warning(f"Failed to get hostname for miner: {self}")
            return "?"
        logging.warning(f"Failed to get hostname for miner: {self}")
        return "?"

    async def get_board_info(self):
        boards_chips = 0
        logging.debug(f"{self}: Getting board info.")
        stats = await self.api.stats()
        if not stats.get("STATS") and not stats.get("STATS") == []:
            print("stats error", stats)
            return {0: [], 1: [], 2: []}
        stats = stats["STATS"][0]
        for key in stats.keys():
            if key.startswith("MM") and not stats[key] == 1:
                data = stats[key]
                for line in data.split("]"):
                    if "TA[" in line:
                        total_chips = line.replace("TA[", "")
                        boards_chips = round(int(total_chips)/3)
        boards = {}
        for board in [0, 1, 2]:
            if not boards_chips == self.nominal_chips:
                nominal = False
            else:
                nominal = True
            boards[board] = []
            boards[board].append({
                    "chain": board,
                    "chip_count": boards_chips,
                    "chip_status": "o" * boards_chips,
                    "nominal": nominal,
                })
        return boards






