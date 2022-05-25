from dataclasses import dataclass, field, asdict


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
    total_chips: int = field(init=False)
    nominal: int = field(init=False)
    pool_split: str = 0
    pool_1_url: str = "Unknown"
    pool_1_user: str = "Unknown"
    pool_2_url: str = ""
    pool_2_user: str = ""

    @property
    def total_chips(self):  # noqa - Skip PyCharm inspection
        return self.right_chips + self.center_chips + self.left_chips

    @total_chips.setter
    def total_chips(self, val):
        pass

    @property
    def nominal(self):  # noqa - Skip PyCharm inspection
        return self.ideal_chips == self.total_chips

    @nominal.setter
    def nominal(self, val):
        pass

    def __post_init__(self):
        self.total_chips = self.right_chips + self.center_chips + self.left_chips
        self.nominal = self.ideal_chips == self.total_chips

    def asdict(self):
        return asdict(self)


if __name__ == "__main__":
    print(MinerData(ip="192.168.1.1").asdict())
