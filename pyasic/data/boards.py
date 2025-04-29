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
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from pyasic.device.algorithm.hashrate import AlgoHashRateType


class HashBoard(BaseModel):
    """A Dataclass to standardize hashboard data.

    Attributes:
        slot: The slot of the board as an int.
        hashrate: The hashrate of the board in TH/s as a float.
        temp: The temperature of the PCB as an int.
        chip_temp: The temperature of the chips as an int.
        chips: The chip count of the board as an int.
        expected_chips: The expected chip count of the board as an int.
        serial_number: The serial number of the board.
        missing: Whether the board is returned from the miners data as a bool.
        tuned: Whether the board is tuned as a bool.
        active: Whether the board is currently tuning as a bool.
        voltage: Current input voltage of the board as a float.
        chip_frequency: Current chip frequency of the board as a float.
    """

    slot: int = 0
    hashrate: AlgoHashRateType | None = None
    temp: float | None = None
    chip_temp: float | None = None
    chips: int | None = None
    expected_chips: int | None = None
    serial_number: str | None = None
    missing: bool = True
    tuned: bool | None = None
    active: bool | None = None
    voltage: float | None = None
    chip_frequency: float | None = None

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

    def as_influxdb(self, key_root: str, level_delimiter: str = ".") -> str:

        def serialize_int(key: str, value: int) -> str:
            return f"{key}={value}"

        def serialize_float(key: str, value: float) -> str:
            return f"{key}={value}"

        def serialize_str(key: str, value: str) -> str:
            return f'{key}="{value}"'

        def serialize_algo_hash_rate(key: str, value: AlgoHashRateType) -> str:
            return f"{key}={round(float(value), 2)}"

        def serialize_bool(key: str, value: bool):
            return f"{key}={str(value).lower()}"

        serialization_map_instance = {
            AlgoHashRateType: serialize_algo_hash_rate,
        }
        serialization_map = {
            int: serialize_int,
            float: serialize_float,
            str: serialize_str,
            bool: serialize_bool,
        }

        include = [
            "hashrate",
            "temp",
            "chip_temp",
            "chips",
            "expected_chips",
            "tuned",
            "active",
            "voltage",
        ]

        field_data = []
        for field in include:
            field_val = getattr(self, field)
            serialization_func = serialization_map.get(
                type(field_val), lambda _k, _v: None
            )
            serialized = serialization_func(
                f"{key_root}{level_delimiter}{field}", field_val
            )
            if serialized is not None:
                field_data.append(serialized)
                continue
            for datatype in serialization_map_instance:
                if serialized is None:
                    if isinstance(field_val, datatype):
                        serialized = serialization_map_instance[datatype](
                            f"{key_root}{level_delimiter}{field}", field_val
                        )
            if serialized is not None:
                field_data.append(serialized)
        return ",".join(field_data)
