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
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class PowerScalingShutdownEnabled:
    mode: str = field(init=False, default="enabled")
    duration: int = None


@dataclass
class PowerScalingShutdownDisabled:
    mode: str = field(init=False, default="disabled")


class PowerScalingShutdown(Enum):
    enabled = PowerScalingShutdownEnabled
    disabled = PowerScalingShutdownDisabled


@dataclass
class PowerScalingEnabled:
    mode: str = field(init=False, default="enabled")
    power_step: int = None
    minimum_power: int = None
    shutdown_mode: PowerScalingShutdown = None


@dataclass
class PowerScalingDisabled:
    mode: str = field(init=False, default="disabled")


class PowerScalingConfig(Enum):
    enabled = PowerScalingEnabled
    disabled = PowerScalingDisabled

    @classmethod
    def default(cls):
        return cls.disabled()

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)
