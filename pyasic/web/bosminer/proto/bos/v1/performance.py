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
from dataclasses import asdict, dataclass
from typing import Union


@dataclass
class Frequency:
    hertz: float


@dataclass
class Voltage:
    volt: float


@dataclass
class Power:
    watt: int


@dataclass
class TeraHashrate:
    terahash_per_second: float


@dataclass
class HashboardPerformanceSettings:
    id: str
    frequency: Frequency
    voltage: Voltage


@dataclass
class ManualPerformanceMode:
    global_frequency: Frequency
    global_voltage: Voltage
    hashboards: list[HashboardPerformanceSettings]


@dataclass
class PowerTargetMode:
    power_target: Power


@dataclass
class HashrateTargetMode:
    hashrate_target: TeraHashrate


@dataclass
class TunerPerformanceMode:
    target: Union[PowerTargetMode, HashrateTargetMode]


@dataclass
class PerformanceMode:
    mode: Union[ManualPerformanceMode, TunerPerformanceMode]

    @classmethod
    def create(
        cls,
        power_target: int = None,
        hashrate_target: float = None,
        manual_configuration: ManualPerformanceMode = None,
    ):
        provided_args = [power_target, hashrate_target, manual_configuration]
        if sum(arg is not None for arg in provided_args) > 1:
            raise ValueError(
                "More than one keyword argument provided. Please use only power target, hashrate target, or manual config."
            )
        elif sum(arg is not None for arg in provided_args) < 1:
            raise ValueError(
                "Please pass one of power target, hashrate target, or manual config."
            )

        if power_target is not None:
            return cls(
                mode=TunerPerformanceMode(
                    target=PowerTargetMode(power_target=Power(watt=power_target))
                )
            )
        elif hashrate_target is not None:
            return cls(
                mode=TunerPerformanceMode(
                    target=HashrateTargetMode(
                        hashrate_target=TeraHashrate(
                            terahash_per_second=hashrate_target
                        )
                    )
                )
            )
        elif manual_configuration is not None:
            return cls(mode=manual_configuration)

    def as_dict(self):
        return asdict(self)
