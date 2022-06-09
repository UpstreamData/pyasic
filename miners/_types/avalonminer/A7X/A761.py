from miners import BaseMiner


class Avalon761(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "Avalon 761"
        self.chip_count = 18  # This miner has 4 boards totaling 72
        self.fan_count = 1  # also only 1 fan
