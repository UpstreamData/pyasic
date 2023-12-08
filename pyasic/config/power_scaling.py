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

from pyasic.config.base import MinerConfigOption, MinerConfigValue


@dataclass
class PowerScalingShutdownEnabled(MinerConfigValue):
    mode: str = field(init=False, default="enabled")
    duration: int = None


@dataclass
class PowerScalingShutdownDisabled(MinerConfigValue):
    mode: str = field(init=False, default="disabled")


class PowerScalingShutdown(MinerConfigOption):
    enabled = PowerScalingShutdownEnabled
    disabled = PowerScalingShutdownDisabled


@dataclass
class PowerScalingEnabled(MinerConfigValue):
    mode: str = field(init=False, default="enabled")
    power_step: int = None
    minimum_power: int = None
    shutdown_mode: PowerScalingShutdown = None


@dataclass
class PowerScalingDisabled(MinerConfigValue):
    mode: str = field(init=False, default="disabled")


class PowerScalingConfig(MinerConfigOption):
    enabled = PowerScalingEnabled
    disabled = PowerScalingDisabled

    @classmethod
    def default(cls):
        return cls.disabled()
