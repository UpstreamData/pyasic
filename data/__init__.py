from dataclasses import dataclass


@dataclass
class MinerData:
    ip: str
    model: str = "Unknown"
    hostname: str = "Unknown"
    hashrate: float = 0
    temperature: float = 0
    wattage: int = 0
    ideal_chips: int = 0
    left_chips: int = 0
    center_chips: int = 0
    right_chips: int = 0
    pool_split: str = 0
    pool_1_url: str = "Unknown"
    pool_1_user: str = "Unknown"
    pool_2_url: str = ""
    pool_2_user: str = ""

    def __post_init__(self):
        self.total_chips = self.right_chips + self.center_chips + self.left_chips
        self.nominal = self.ideal_chips == self.total_chips

    def asdict(self):
        return {k: v for k, v in self.__dict__.items()}
