from miner_interface.miners import BaseMiner


class Avalon741(BaseMiner):
    def __init__(self, ip: str):
        super().__init__()
        self.ip = ip
        self.model = "Avalon 741"
        self.chip_count = 22  # This miner has 4 boards totaling 88
        self.fan_count = 1  # also only 1 fan
