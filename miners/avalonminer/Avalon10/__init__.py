from miners.cgminer import CGMiner
import logging


class CGMinerAvalon10(CGMiner):
    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.model = "Avalon 10"
        self.api_type = "CGMiner"

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
