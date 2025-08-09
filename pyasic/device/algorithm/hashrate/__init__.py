from .base import AlgoHashRateType
from .blake256 import Blake256HashRate
from .blockflow import BlockFlowHashRate
from .eaglesong import EaglesongHashRate
from .equihash import EquihashHashRate
from .ethash import EtHashHashRate
from .handshake import HandshakeHashRate
from .kadena import KadenaHashRate
from .kheavyhash import KHeavyHashHashRate
from .scrypt import ScryptHashRate
from .sha256 import SHA256HashRate
from .x11 import X11HashRate
from .zksnark import ZkSnarkHashRate


class AlgoHashRate:
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
    BLOCKFLOW = BlockFlowHashRate
    ZKSNARK = ZkSnarkHashRate
