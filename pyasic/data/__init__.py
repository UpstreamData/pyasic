#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Union
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class MinerData:
    """A Dataclass to standardize data returned from miners (specifically `AnyMiner().get_data()`)

    Attributes:
        ip: The IP of the miner as a str.
        datetime: The time and date this data was generated.
        model: The model of the miner as a str.
        hostname: The network hostname of the miner as a str.
        hashrate: The hashrate of the miner in TH/s as a float.
        left_board_hashrate: The hashrate of the left board of the miner in TH/s as a float.
        center_board_hashrate: The hashrate of the center board of the miner in TH/s as a float.
        right_board_hashrate: The hashrate of the right board of the miner in TH/s as a float.
        temperature_avg: The average temperature across the boards.  Calculated automatically.
        env_temp: The environment temps as a float.
        left_board_temp: The temp of the left PCB as an int.
        left_board_chip_temp: The temp of the left board chips as an int.
        center_board_temp: The temp of the center PCB as an int.
        center_board_chip_temp: The temp of the center board chips as an int.
        right_board_temp: The temp of the right PCB as an int.
        right_board_chip_temp: The temp of the right board chips as an int.
        wattage: Current power draw of the miner as an int.
        wattage_limit: Power limit of the miner as an int.
        fan_1: The speed of the first fan as an int.
        fan_2: The speed of the second fan as an int.
        fan_3: The speed of the third fan as an int.
        fan_4: The speed of the fourth fan as an int.
        left_chips: The number of chips online in the left board as an int.
        center_chips: The number of chips online in the left board as an int.
        right_chips: The number of chips online in the left board as an int.
        total_chips: The total number of chips on all boards.  Calculated automatically.
        ideal_chips: The ideal number of chips in the miner as an int.
        percent_ideal: The percent of total chips out of the ideal count.  Calculated automatically.
        nominal: The nominal amount of chips in the miner.  Calculated automatically.
        pool_split: The pool split as a str.
        pool_1_url: The first pool url on the miner as a str.
        pool_1_user: The first pool user on the miner as a str.
        pool_2_url: The second pool url on the miner as a str.
        pool_2_user: The second pool user on the miner as a str.
        errors: A list of errors on the miner.
    """

    ip: str
    datetime: datetime = None
    mac: str = "00:00:00:00:00:00"
    model: str = "Unknown"
    hostname: str = "Unknown"
    hashrate: float = 0
    left_board_hashrate: float = 0
    center_board_hashrate: float = 0
    right_board_hashrate: float = 0
    temperature_avg: int = field(init=False)
    env_temp: float = 0
    left_board_temp: int = 0
    left_board_chip_temp: int = 0
    center_board_temp: int = 0
    center_board_chip_temp: int = 0
    right_board_temp: int = 0
    right_board_chip_temp: int = 0
    wattage: int = 0
    wattage_limit: int = 0
    fan_1: int = -1
    fan_2: int = -1
    fan_3: int = -1
    fan_4: int = -1
    left_chips: int = 0
    center_chips: int = 0
    right_chips: int = 0
    total_chips: int = field(init=False)
    ideal_chips: int = 1
    percent_ideal: float = field(init=False)
    nominal: int = field(init=False)
    pool_split: str = "0"
    pool_1_url: str = "Unknown"
    pool_1_user: str = "Unknown"
    pool_2_url: str = ""
    pool_2_user: str = ""
    errors: list = field(default_factory=list)
    fault_light: Union[bool, None] = None

    def __post_init__(self):
        self.datetime = datetime.now()

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

    @property
    def percent_ideal(self):  # noqa - Skip PyCharm inspection
        return round((self.total_chips / self.ideal_chips) * 100)

    @percent_ideal.setter
    def percent_ideal(self, val):
        pass

    @property
    def temperature_avg(self):  # noqa - Skip PyCharm inspection
        total_temp = 0
        temp_count = 0
        for temp in [
            self.left_board_chip_temp,
            self.center_board_chip_temp,
            self.right_board_chip_temp,
        ]:
            if temp and not temp == 0:
                total_temp += temp
                temp_count += 1
        if not temp_count > 0:
            return 0
        return round(total_temp / temp_count)

    @temperature_avg.setter
    def temperature_avg(self, val):
        pass

    def asdict(self):
        return asdict(self)
