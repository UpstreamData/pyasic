from .blake256 import Blake256Unit
from .eaglesong import EaglesongUnit
from .equihash import EquihashUnit
from .ethash import EtHashUnit
from .handshake import HandshakeUnit
from .kadena import KadenaUnit
from .kheavyhash import KHeavyHashUnit
from .scrypt import ScryptUnit
from .sha256 import SHA256Unit
from .x11 import X11Unit


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
