# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

import copy
import json
import logging
import time
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from typing import Any, List, Union

from .error_codes import BraiinsOSError, InnosiliconError, WhatsminerError, X19Error


@dataclass
class HashBoard:
    """A Dataclass to standardize hashboard data.

    Attributes:
        slot: The slot of the board as an int.
        hashrate: The hashrate of the board in TH/s as a float.
        temp: The temperature of the PCB as an int.
        chip_temp: The temperature of the chips as an int.
        chips: The chip count of the board as an int.
        expected_chips: The ideal chip count of the board as an int.
        missing: Whether the board is returned from the miners data as a bool.
    """

    slot: int = 0
    hashrate: float = None
    temp: int = None
    chip_temp: int = None
    chips: int = None
    expected_chips: int = None
    missing: bool = True

    def get(self, __key: str, default: Any = None):
        try:
            val = self.__getitem__(__key)
            if val is None:
                return default
            return val
        except KeyError:
            return default

    def __getitem__(self, item: str):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(f"{item}")


@dataclass
class Fan:
    """A Dataclass to standardize fan data.

    Attributes:
        speed: The speed of the fan.
    """

    speed: int = None

    def get(self, __key: str, default: Any = None):
        try:
            val = self.__getitem__(__key)
            if val is None:
                return default
            return val
        except KeyError:
            return default

    def __getitem__(self, item: str):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(f"{item}")


@dataclass
class MinerData:
    """A Dataclass to standardize data returned from miners (specifically `AnyMiner().get_data()`)

    Attributes:
        ip: The IP of the miner as a str.
        datetime: The time and date this data was generated.
        uptime: The uptime of the miner in seconds.
        mac: The MAC address of the miner as a str.
        model: The model of the miner as a str.
        make: The make of the miner as a str.
        api_ver: The current api version on the miner as a str.
        fw_ver: The current firmware version on the miner as a str.
        hostname: The network hostname of the miner as a str.
        hashrate: The hashrate of the miner in TH/s as a float.  Calculated automatically.
        _hashrate: Backup for hashrate found via API instead of hashboards.
        nominal_hashrate: The factory nominal hashrate of the miner in TH/s as a float.
        hashboards: A list of hashboards on the miner with their statistics.
        temperature_avg: The average temperature across the boards.  Calculated automatically.
        env_temp: The environment temps as a float.
        wattage: Current power draw of the miner as an int.
        wattage_limit: Power limit of the miner as an int.
        fans: A list of fans on the miner with their speeds.
        fan_psu: The speed of the PSU on the fan if the miner collects it.
        total_chips: The total number of chips on all boards.  Calculated automatically.
        ideal_chips: The ideal number of chips in the miner as an int.
        percent_ideal_chips: The percent of total chips out of the ideal count.  Calculated automatically.
        percent_ideal_hashrate: The percent of total hashrate out of the ideal hashrate.  Calculated automatically.
        percent_ideal_wattage: The percent of total wattage out of the ideal wattage.  Calculated automatically.
        nominal: Whether the number of chips in the miner is nominal.  Calculated automatically.
        pool_split: The pool split as a str.
        pool_1_url: The first pool url on the miner as a str.
        pool_1_user: The first pool user on the miner as a str.
        pool_2_url: The second pool url on the miner as a str.
        pool_2_user: The second pool user on the miner as a str.
        errors: A list of errors on the miner.
        fault_light: Whether the fault light is on as a boolean.
        efficiency: Efficiency of the miner in J/TH (Watts per TH/s).  Calculated automatically.
        is_mining: Whether the miner is mining.
    """

    ip: str
    datetime: datetime = None
    uptime: int = None
    mac: str = None
    model: str = None
    make: str = None
    api_ver: str = None
    fw_ver: str = None
    hostname: str = None
    hashrate: float = field(init=False)
    _hashrate: float = None
    nominal_hashrate: float = None
    hashboards: List[HashBoard] = field(default_factory=list)
    ideal_hashboards: int = None
    temperature_avg: int = field(init=False)
    env_temp: float = None
    wattage: int = None
    wattage_limit: int = None
    fans: List[Fan] = field(default_factory=list)
    fan_psu: int = None
    total_chips: int = field(init=False)
    ideal_chips: int = None
    percent_ideal_chips: float = field(init=False)
    percent_ideal_hashrate: float = field(init=False)
    percent_ideal_wattage: float = field(init=False)
    nominal: bool = field(init=False)
    pool_split: str = "0"
    pool_1_url: str = "Unknown"
    pool_1_user: str = "Unknown"
    pool_2_url: str = ""
    pool_2_user: str = ""
    errors: List[
        Union[WhatsminerError, BraiinsOSError, X19Error, InnosiliconError]
    ] = field(default_factory=list)
    fault_light: Union[bool, None] = None
    efficiency: int = field(init=False)
    is_mining: bool = True

    @classmethod
    def fields(cls):
        return [f.name for f in fields(cls)]

    def __post_init__(self):
        self.datetime = datetime.now(timezone.utc).astimezone()

    def get(self, __key: str, default: Any = None):
        try:
            val = self.__getitem__(__key)
            if val is None:
                return default
            return val
        except KeyError:
            return default

    def __getitem__(self, item: str):
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(f"{item}")

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __iter__(self):
        return iter([item for item in self.asdict()])

    def __truediv__(self, other):
        return self // other

    def __floordiv__(self, other):
        cp = copy.deepcopy(self)
        for key in self:
            item = getattr(self, key)
            if isinstance(item, int):
                setattr(cp, key, item // other)
            if isinstance(item, float):
                setattr(cp, key, round(item / other, 2))
        return cp

    def __add__(self, other):
        if not isinstance(other, MinerData):
            raise TypeError("Cannot add MinerData to non MinerData type.")
        cp = copy.deepcopy(self)
        for key in self:
            item = getattr(self, key)
            other_item = getattr(other, key)
            if item is None:
                item = 0
            if other_item is None:
                other_item = 0

            if isinstance(item, int):
                setattr(cp, key, item + other_item)
            if isinstance(item, float):
                setattr(cp, key, item + other_item)
            if isinstance(item, str):
                setattr(cp, key, "")
            if isinstance(item, list):
                setattr(cp, key, item + other_item)
            if isinstance(item, bool):
                setattr(cp, key, item & other_item)
        return cp

    @property
    def hashrate(self):  # noqa - Skip PyCharm inspection
        if len(self.hashboards) > 0:
            hr_data = []
            for item in self.hashboards:
                if item.hashrate is not None:
                    hr_data.append(item.hashrate)
            if len(hr_data) > 0:
                return sum(hr_data)
        return self._hashrate

    @hashrate.setter
    def hashrate(self, val):
        self._hashrate = val

    @property
    def total_chips(self):  # noqa - Skip PyCharm inspection
        if len(self.hashboards) > 0:
            chip_data = []
            for item in self.hashboards:
                if item.chips is not None:
                    chip_data.append(item.chips)
            if len(chip_data) > 0:
                return sum(chip_data)
            return None

    @total_chips.setter
    def total_chips(self, val):
        pass

    @property
    def nominal(self):  # noqa - Skip PyCharm inspection
        if self.total_chips is None or self.ideal_chips is None:
            return None
        return self.ideal_chips == self.total_chips

    @nominal.setter
    def nominal(self, val):
        pass

    @property
    def percent_ideal_chips(self):  # noqa - Skip PyCharm inspection
        if self.total_chips is None or self.ideal_chips is None:
            return None
        if self.total_chips == 0 or self.ideal_chips == 0:
            return 0
        return round((self.total_chips / self.ideal_chips) * 100)

    @percent_ideal_chips.setter
    def percent_ideal_chips(self, val):
        pass

    @property
    def percent_ideal_hashrate(self):  # noqa - Skip PyCharm inspection
        if self.hashrate is None or self.nominal_hashrate is None:
            return None
        if self.hashrate == 0 or self.nominal_hashrate == 0:
            return 0
        return round((self.hashrate / self.nominal_hashrate) * 100)

    @percent_ideal_hashrate.setter
    def percent_ideal_hashrate(self, val):
        pass

    @property
    def percent_ideal_wattage(self):  # noqa - Skip PyCharm inspection
        if self.wattage_limit is None or self.wattage is None:
            return None
        if self.wattage_limit == 0 or self.wattage == 0:
            return 0
        return round((self.wattage / self.wattage_limit) * 100)

    @percent_ideal_wattage.setter
    def percent_ideal_wattage(self, val):
        pass

    @property
    def temperature_avg(self):  # noqa - Skip PyCharm inspection
        total_temp = 0
        temp_count = 0
        for hb in self.hashboards:
            if hb.temp is not None:
                total_temp += hb.temp
                temp_count += 1
        if not temp_count > 0:
            return None
        return round(total_temp / temp_count)

    @temperature_avg.setter
    def temperature_avg(self, val):
        pass

    @property
    def efficiency(self):  # noqa - Skip PyCharm inspection
        if self.hashrate is None or self.wattage is None:
            return None
        if self.hashrate == 0 or self.wattage == 0:
            return 0
        return round(self.wattage / self.hashrate)

    @efficiency.setter
    def efficiency(self, val):
        pass

    def asdict(self) -> dict:
        """Get this dataclass as a dictionary.

        Returns:
            A dictionary version of this class.
        """
        logging.debug(f"MinerData - (To Dict) - Dumping Dict data")
        return asdict(self)

    def as_json(self) -> str:
        """Get this dataclass as JSON.

        Returns:
            A JSON version of this class.
        """
        logging.debug(f"MinerData - (To JSON) - Dumping JSON data")
        data = self.asdict()
        data["datetime"] = str(int(time.mktime(data["datetime"].timetuple())))
        return json.dumps(data)

    def as_csv(self) -> str:
        """Get this dataclass as CSV.

        Returns:
            A CSV version of this class with no headers.
        """
        logging.debug(f"MinerData - (To CSV) - Dumping CSV data")
        data = self.asdict()
        data["datetime"] = str(int(time.mktime(data["datetime"].timetuple())))
        errs = []
        for error in data["errors"]:
            errs.append(error["error_message"])
        data["errors"] = "; ".join(errs)
        data_list = [str(data[item]) for item in data]
        return ",".join(data_list)

    def as_influxdb(self, measurement_name: str = "miner_data") -> str:
        """Get this dataclass as [influxdb line protocol](https://docs.influxdata.com/influxdb/v2.4/reference/syntax/line-protocol/).

        Parameters:
            measurement_name: The name of the measurement to insert into in influxdb.

        Returns:
            A influxdb line protocol version of this class.
        """
        logging.debug(f"MinerData - (To InfluxDB) - Dumping InfluxDB data")
        tag_data = [measurement_name]
        field_data = []

        tags = ["ip", "mac", "model", "hostname"]
        for attribute in self:
            if attribute in tags:
                escaped_data = self.get(attribute, "Unknown").replace(" ", "\\ ")
                tag_data.append(f"{attribute}={escaped_data}")
                continue
            elif str(attribute).startswith("_"):
                continue
            elif isinstance(self[attribute], str):
                field_data.append(f'{attribute}="{self[attribute]}"')
                continue
            elif isinstance(self[attribute], bool):
                field_data.append(f"{attribute}={str(self[attribute]).lower()}")
                continue
            elif isinstance(self[attribute], int):
                field_data.append(f"{attribute}={self[attribute]}")
                continue
            elif isinstance(self[attribute], float):
                field_data.append(f"{attribute}={self[attribute]}")
                continue
            elif attribute == "errors":
                for idx, item in enumerate(self[attribute]):
                    field_data.append(f'error_{idx+1}="{item.error_message}"')
            elif attribute == "hashboards":
                for idx, item in enumerate(self[attribute]):
                    field_data.append(
                        f"hashboard_{idx+1}_hashrate={item.get('hashrate', 0.0)}"
                    )
                    field_data.append(
                        f"hashboard_{idx+1}_temperature={item.get('temp', 0)}"
                    )
                    field_data.append(
                        f"hashboard_{idx+1}_chip_temperature={item.get('chip_temp', 0)}"
                    )
                    field_data.append(f"hashboard_{idx+1}_chips={item.get('chips', 0)}")
                    field_data.append(
                        f"hashboard_{idx+1}_expected_chips={item.get('expected_chips', 0)}"
                    )
            elif attribute == "fans":
                for idx, item in enumerate(self[attribute]):
                    if item.speed is not None:
                        field_data.append(f"fan_{idx+1}={item.speed}")

        tags_str = ",".join(tag_data)
        field_str = ",".join(field_data)
        timestamp = str(int(time.mktime(self.datetime.timetuple()) * 1e9))

        return " ".join([tags_str, field_str, timestamp])
