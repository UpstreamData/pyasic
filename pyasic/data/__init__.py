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
import time
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, computed_field

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModePowerTune
from pyasic.data.pools import PoolMetrics, Scheme
from pyasic.device.algorithm.hashrate import AlgoHashRateType

from .boards import HashBoard
from .device import DeviceInfo
from .error_codes import BraiinsOSError, InnosiliconError, WhatsminerError, X19Error
from .error_codes.base import BaseMinerError
from .fans import Fan


class MinerData(BaseModel):
    """A Dataclass to standardize data returned from miners (specifically `AnyMiner().get_data()`)

    Attributes:
        ip: The IP of the miner as a str.
        datetime: The time and date this data was generated.
        uptime: The uptime of the miner in seconds.
        mac: The MAC address of the miner as a str.
        device_info: Info about the device, such as model, make, and firmware.
        model: The model of the miner as a str.
        make: The make of the miner as a str.
        firmware: The firmware on the miner as a str.
        algo: The mining algorithm of the miner as a str.
        api_ver: The current api version on the miner as a str.
        fw_ver: The current firmware version on the miner as a str.
        hostname: The network hostname of the miner as a str.
        hashrate: The hashrate of the miner in TH/s as a float.  Calculated automatically.
        expected_hashrate: The factory nominal hashrate of the miner in TH/s as a float.
        sticker_hashrate: The factory sticker hashrate of the miner as a float.
        hashboards: A list of [`HashBoard`][pyasic.data.HashBoard]s on the miner with their statistics.
        temperature_avg: The average temperature across the boards.  Calculated automatically.
        env_temp: The environment temps as a float.
        wattage: Current power draw of the miner as an int.
        voltage: Current output voltage of the PSU as an float.
        wattage_limit: Power limit of the miner as an int.
        fans: A list of fans on the miner with their speeds.
        expected_fans: The number of fans expected on a miner.
        fan_psu: The speed of the PSU on the fan if the miner collects it.
        total_chips: The total number of chips on all boards.  Calculated automatically.
        expected_chips: The expected number of chips in the miner as an int.
        percent_expected_chips: The percent of total chips out of the expected count.  Calculated automatically.
        percent_expected_hashrate: The percent of total hashrate out of the expected hashrate.  Calculated automatically.
        percent_expected_wattage: The percent of total wattage out of the expected wattage.  Calculated automatically.
        nominal: Whether the number of chips in the miner is nominal.  Calculated automatically.
        config: The parsed config of the miner, using [`MinerConfig`][pyasic.config.MinerConfig].
        errors: A list of errors on the miner.
        fault_light: Whether the fault light is on as a boolean.
        efficiency: Efficiency of the miner in J/TH (Watts per TH/s).  Calculated automatically.
        is_mining: Whether the miner is mining.
        pools: A list of PoolMetrics instances, each representing metrics for a pool.
    """

    # general
    ip: str
    raw_datetime: datetime = Field(
        exclude=True, default_factory=datetime.now(timezone.utc).astimezone, repr=False
    )

    # about
    device_info: DeviceInfo | None = None
    mac: str | None = None
    api_ver: str | None = None
    fw_ver: str | None = None
    hostname: str | None = None

    # hashrate
    raw_hashrate: AlgoHashRateType = Field(exclude=True, default=None, repr=False)

    # sticker
    sticker_hashrate: AlgoHashRateType | None = None

    # expected
    expected_hashrate: AlgoHashRateType | None = None
    expected_hashboards: int | None = None
    expected_chips: int | None = None
    expected_fans: int | None = None

    # temperature
    env_temp: float | None = None

    # power
    wattage: int | None = None
    voltage: float | None = None
    raw_wattage_limit: int | None = Field(exclude=True, default=None, repr=False)

    # fans
    fans: list[Fan] = Field(default_factory=list)
    fan_psu: int | None = None

    # boards
    hashboards: list[HashBoard] = Field(default_factory=list)

    # config
    config: MinerConfig | None = None
    fault_light: bool | None = None

    # errors
    errors: list[BaseMinerError] = Field(default_factory=list)

    # mining state
    is_mining: bool = True
    uptime: int | None = None

    # pools
    pools: list[PoolMetrics] = Field(default_factory=list)

    @classmethod
    def fields(cls) -> set:
        all_fields = set(cls.model_fields.keys())
        all_fields.update(set(cls.model_computed_fields.keys()))
        return all_fields

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
        for key in self.fields():
            item = getattr(self, key)
            if isinstance(item, int):
                setattr(cp, key, item // other)
            if isinstance(item, float):
                setattr(cp, key, item / other)
        return cp

    def __add__(self, other):
        if not isinstance(other, MinerData):
            raise TypeError("Cannot add MinerData to non MinerData type.")
        cp = copy.deepcopy(self)
        for key in self.fields():
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

    @computed_field  # type: ignore[misc]
    @property
    def hashrate(self) -> AlgoHashRateType | None:
        raw_hashrate = self.raw_hashrate
        calc_hashrate = None
        if len(self.hashboards) > 0:
            hr_data = []
            for item in self.hashboards:
                if item.hashrate is not None:
                    hr_data.append(item.hashrate)
            if len(hr_data) > 0:
                calc_hashrate = sum(
                    hr_data, start=self.device_info.algo.hashrate(rate=0)
                )
        if raw_hashrate is not None and calc_hashrate is not None:
            return (
                raw_hashrate if raw_hashrate > calc_hashrate else calc_hashrate
            )  # always return the larger one
        return raw_hashrate if raw_hashrate is not None else calc_hashrate

    @hashrate.setter
    def hashrate(self, val):
        self.raw_hashrate = val

    @computed_field  # type: ignore[misc]
    @property
    def wattage_limit(self) -> int | None:
        if self.config is not None:
            if isinstance(self.config.mining_mode, MiningModePowerTune):
                return self.config.mining_mode.power
        return self.raw_wattage_limit

    @wattage_limit.setter
    def wattage_limit(self, val: int):
        self.raw_wattage_limit = val

    @computed_field  # type: ignore[misc]
    @property
    def total_chips(self) -> int | None:
        if len(self.hashboards) > 0:
            chip_data = []
            for item in self.hashboards:
                if item.chips is not None:
                    chip_data.append(item.chips)
            if len(chip_data) > 0:
                return sum(chip_data)
            return None

    @computed_field  # type: ignore[misc]
    @property
    def nominal(self) -> bool | None:
        if self.total_chips is None or self.expected_chips is None:
            return None
        return self.expected_chips == self.total_chips

    @computed_field  # type: ignore[misc]
    @property
    def percent_expected_chips(self) -> int | None:
        if self.total_chips is None or self.expected_chips is None:
            return None
        if self.total_chips == 0 or self.expected_chips == 0:
            return 0
        return round((self.total_chips / self.expected_chips) * 100)

    @computed_field  # type: ignore[misc]
    @property
    def percent_expected_hashrate(self) -> int | None:
        if self.hashrate is None or self.expected_hashrate is None:
            return None
        try:
            return round((self.hashrate / self.expected_hashrate) * 100)
        except ZeroDivisionError:
            return 0

    @computed_field  # type: ignore[misc]
    @property
    def percent_expected_wattage(self) -> int | None:
        if self.wattage_limit is None or self.wattage is None:
            return None
        try:
            return round((self.wattage / self.wattage_limit) * 100)
        except ZeroDivisionError:
            return 0

    @computed_field  # type: ignore[misc]
    @property
    def temperature_avg(self) -> int | None:
        total_temp = 0
        temp_count = 0
        for hb in self.hashboards:
            if hb.temp is not None:
                total_temp += hb.temp
                temp_count += 1
        if not temp_count > 0:
            return None
        return round(total_temp / temp_count)

    @computed_field  # type: ignore[misc]
    @property
    def efficiency(self) -> int | None:
        if self.hashrate is None or self.wattage is None:
            return None
        try:
            return round(self.wattage / float(self.hashrate))
        except ZeroDivisionError:
            return 0

    @computed_field  # type: ignore[misc]
    @property
    def datetime(self) -> str:
        return self.raw_datetime.isoformat()

    @computed_field  # type: ignore[misc]
    @property
    def timestamp(self) -> int:
        return int(time.mktime(self.raw_datetime.timetuple()))

    @computed_field  # type: ignore[misc]
    @property
    def make(self) -> str | None:
        if self.device_info.make is not None:
            return str(self.device_info.make)

    @computed_field  # type: ignore[misc]
    @property
    def model(self) -> str | None:
        if self.device_info.model is not None:
            return str(self.device_info.model)

    @computed_field  # type: ignore[misc]
    @property
    def firmware(self) -> str | None:
        if self.device_info.firmware is not None:
            return str(self.device_info.firmware)

    @computed_field  # type: ignore[misc]
    @property
    def algo(self) -> str | None:
        if self.device_info.algo is not None:
            return str(self.device_info.algo)

    def keys(self) -> list:
        return list(self.model_fields.keys())

    def asdict(self) -> dict:
        return self.model_dump()

    def as_dict(self) -> dict:
        """Get this dataclass as a dictionary.

        Returns:
            A dictionary version of this class.
        """
        return self.asdict()

    def as_json(self) -> str:
        """Get this dataclass as JSON.

        Returns:
            A JSON version of this class.
        """
        return self.model_dump_json()

    def as_csv(self) -> str:
        """Get this dataclass as CSV.

        Returns:
            A CSV version of this class with no headers.
        """
        data = self.asdict()
        errs = []
        for error in data["errors"]:
            errs.append(error["error_message"])
        data["errors"] = "; ".join(errs)
        data_list = [str(data[item]) for item in data]
        return ",".join(data_list)

    def as_influxdb(
        self, measurement_name: str = "miner_data", level_delimiter: str = "."
    ) -> str:
        """Get this dataclass as [influxdb line protocol](https://docs.influxdata.com/influxdb/v2.4/reference/syntax/line-protocol/).

        Parameters:
            measurement_name: The name of the measurement to insert into in influxdb.

        Returns:
            A influxdb line protocol version of this class.
        """

        def serialize_int(key: str, value: int) -> str:
            return f"{key}={value}"

        def serialize_float(key: str, value: float) -> str:
            return f"{key}={value}"

        def serialize_str(key: str, value: str) -> str:
            return f'{key}="{value}"'

        def serialize_algo_hash_rate(key: str, value: AlgoHashRateType) -> str:
            return f"{key}={round(float(value), 2)}"

        def serialize_list(key: str, value: list[Any]) -> str | None:
            if len(value) == 0:
                return None

            list_field_data = []
            for idx, list_field_val in enumerate(value):
                item_serialization_func = serialization_map.get(
                    type(list_field_val), lambda _k, _v: None
                )
                item_serialized = item_serialization_func(
                    f"{key}{level_delimiter}{idx}", list_field_val
                )
                if item_serialized is not None:
                    list_field_data.append(item_serialized)
                    continue
                for dt in serialization_map_instance:
                    if item_serialized is None:
                        if isinstance(list_field_val, dt):
                            item_serialized = serialization_map_instance[dt](
                                f"{key}{level_delimiter}{idx}", list_field_val
                            )
                if item_serialized is not None:
                    list_field_data.append(item_serialized)
            return ",".join(list_field_data)

        def serialize_miner_error(key: str, value: BaseMinerError):
            return value.as_influxdb(key, level_delimiter=level_delimiter)

        def serialize_fan(key: str, value: Fan) -> str:
            return f"{key}{level_delimiter}speed={value.speed}"

        def serialize_hashboard(key: str, value: HashBoard) -> str:
            return value.as_influxdb(key, level_delimiter=level_delimiter)

        def serialize_bool(key: str, value: bool):
            return f"{key}={str(value).lower()}"

        def serialize_pool_metrics(key: str, value: PoolMetrics):
            return value.as_influxdb(key, level_delimiter=level_delimiter)

        include = [
            "uptime",
            "expected_hashrate",
            "hashrate",
            "hashboards",
            "temperature_avg",
            "env_temp",
            "wattage",
            "wattage_limit",
            "voltage",
            "fans",
            "expected_fans",
            "fan_psu",
            "total_chips",
            "expected_chips",
            "efficiency",
            "fault_light",
            "is_mining",
            "errors",
            "pools",
        ]

        serialization_map_instance = {
            AlgoHashRateType: serialize_algo_hash_rate,
            BaseMinerError: serialize_miner_error,
        }
        serialization_map = {
            int: serialize_int,
            float: serialize_float,
            str: serialize_str,
            bool: serialize_bool,
            list: serialize_list,
            Fan: serialize_fan,
            HashBoard: serialize_hashboard,
            PoolMetrics: serialize_pool_metrics,
        }

        tag_data = [
            measurement_name,
            f"ip={str(self.ip)}",
            f"mac={str(self.mac)}",
            f"make={str(self.make)}",
            f"model={str(self.model)}",
            f"firmware={str(self.firmware)}",
            f"algo={str(self.algo)}",
        ]
        field_data = []

        for field in include:
            field_val = getattr(self, field)
            serialization_func = serialization_map.get(
                type(field_val), lambda _k, _v: None
            )
            serialized = serialization_func(field, field_val)
            if serialized is not None:
                field_data.append(serialized)
                continue
            for datatype in serialization_map_instance:
                if serialized is None:
                    if isinstance(field_val, datatype):
                        serialized = serialization_map_instance[datatype](
                            field, field_val
                        )
            if serialized is not None:
                field_data.append(serialized)

        tags_str = ",".join(tag_data).replace(" ", "\\ ")
        field_str = ",".join(field_data).replace(" ", "\\ ")
        timestamp = str(self.timestamp * 10**9)

        return " ".join([tags_str, field_str, timestamp])
