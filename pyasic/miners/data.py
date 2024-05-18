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

from dataclasses import dataclass, field, make_dataclass
from enum import Enum
from typing import List, Union


class DataOptions(Enum):
    MAC = "mac"
    API_VERSION = "api_ver"
    FW_VERSION = "fw_ver"
    HOSTNAME = "hostname"
    HASHRATE = "hashrate"
    EXPECTED_HASHRATE = "expected_hashrate"
    HASHBOARDS = "hashboards"
    ENVIRONMENT_TEMP = "env_temp"
    WATTAGE = "wattage"
    WATTAGE_LIMIT = "wattage_limit"
    FANS = "fans"
    FAN_PSU = "fan_psu"
    ERRORS = "errors"
    FAULT_LIGHT = "fault_light"
    IS_MINING = "is_mining"
    UPTIME = "uptime"
    CONFIG = "config"
    POOLS = "pools"

    def __str__(self):
        return self.value

    def default_command(self):
        if str(self.value) == "config":
            return "get_config"
        elif str(self.value) == "is_mining":
            return "_is_mining"
        else:
            return f"_get_{str(self.value)}"


@dataclass
class RPCAPICommand:
    name: str
    cmd: str


@dataclass
class WebAPICommand:
    name: str
    cmd: str


@dataclass
class DataFunction:
    cmd: str
    kwargs: List[Union[RPCAPICommand, WebAPICommand]] = field(default_factory=list)

    def __call__(self, *args, **kwargs):
        return self


DataLocations = make_dataclass(
    "DataLocations",
    [
        (
            enum_value.value,
            DataFunction,
            field(default_factory=DataFunction(enum_value.default_command())),
        )
        for enum_value in DataOptions
    ],
)
