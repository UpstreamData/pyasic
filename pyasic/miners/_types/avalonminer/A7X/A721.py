from pyasic.miners import BaseMiner


class Avalon721(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "Avalon 721"
        self.chip_count = 18  # This miner has 4 boards totaling 72
        self.fan_count = 1  # also only 1 fan
