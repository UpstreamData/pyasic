from enum import Enum

from pyasic.data.hashrate.sha256 import SHA256HashRate
from pyasic.device.algorithm.sha256 import SHA256Unit


class AlgoHashRate(Enum):
    SHA256 = SHA256HashRate

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)


class HashUnit:
    SHA256 = SHA256Unit
