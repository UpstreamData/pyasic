from enum import Enum

from pyasic.data.hashrate.base import AlgoHashRateType
from pyasic.data.hashrate.blake256 import Blake256HashRate
from pyasic.data.hashrate.eaglesong import EaglesongHashRate
from pyasic.data.hashrate.equihash import EquihashHashRate
from pyasic.data.hashrate.ethash import EtHashHashRate
from pyasic.data.hashrate.handshake import HandshakeHashRate
from pyasic.data.hashrate.kadena import KadenaHashRate
from pyasic.data.hashrate.kheavyhash import KHeavyHashHashRate
from pyasic.data.hashrate.scrypt import ScryptHashRate
from pyasic.data.hashrate.sha256 import SHA256HashRate
from pyasic.data.hashrate.x11 import X11HashRate
from pyasic.device.algorithm.blake256 import Blake256Unit
from pyasic.device.algorithm.eaglesong import EaglesongUnit
from pyasic.device.algorithm.equihash import EquihashUnit
from pyasic.device.algorithm.ethash import EtHashUnit
from pyasic.device.algorithm.handshake import HandshakeUnit
from pyasic.device.algorithm.kadena import KadenaUnit
from pyasic.device.algorithm.kheavyhash import KHeavyHashUnit
from pyasic.device.algorithm.scrypt import ScryptUnit
from pyasic.device.algorithm.sha256 import SHA256Unit
from pyasic.device.algorithm.x11 import X11Unit


class AlgoHashRate(Enum):
    SHA256 = SHA256HashRate
    SCRYPT = ScryptHashRate
    KHEAVYHASH = KHeavyHashHashRate
    KADENA = KadenaHashRate
    HANDSHAKE = HandshakeHashRate
    X11 = X11HashRate
    BLAKE256 = Blake256HashRate
    EAGLESONG = EaglesongHashRate
    ETHASH = EtHashHashRate
    EQUIHASH = EquihashHashRate

    def __call__(self, *args, **kwargs):
        return self.value(*args, **kwargs)


class HashUnit:
    SHA256 = SHA256Unit
    SCRYPT = ScryptUnit
    KHEAVYHASH = KHeavyHashUnit
    KADENA = KadenaUnit
    HANDSHAKE = HandshakeUnit
    X11 = X11Unit
    BLAKE256 = Blake256Unit
    EAGLESONG = EaglesongUnit
    ETHASH = EtHashUnit
    EQUIHASH = EquihashUnit
