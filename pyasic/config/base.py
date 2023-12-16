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
from enum import Enum
from typing import Union


class MinerConfigOption(Enum):
    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]):
        return cls.default()

    def as_am_modern(self) -> dict:
        return self.value.as_am_modern()

    def as_am_old(self) -> dict:
        return self.value.as_am_old()

    def as_wm(self) -> dict:
        return self.value.as_wm()

    def as_inno(self) -> dict:
        return self.value.as_inno()

    def as_goldshell(self) -> dict:
        return self.value.as_goldshell()

    def as_avalon(self) -> dict:
        return self.value.as_avalon()

    def as_bosminer(self) -> dict:
        return self.value.as_bosminer()

    def as_bos_grpc(self) -> dict:
        return self.value.as_bos_grpc()

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)

    @classmethod
    def default(cls):
        pass


@dataclass
class MinerConfigValue:
    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]):
        return cls()

    def as_dict(self):
        return asdict(self)

    def as_am_modern(self) -> dict:
        return {}

    def as_am_old(self) -> dict:
        return {}

    def as_wm(self) -> dict:
        return {}

    def as_inno(self) -> dict:
        return {}

    def as_goldshell(self) -> dict:
        return {}

    def as_avalon(self) -> dict:
        return {}

    def as_bosminer(self) -> dict:
        return {}

    def as_bos_grpc(self) -> dict:
        return {}
