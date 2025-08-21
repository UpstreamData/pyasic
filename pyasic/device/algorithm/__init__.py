from .base import MinerAlgoType
from .blake256 import Blake256Algo
from .blockflow import BlockFlowAlgo
from .eaglesong import EaglesongAlgo
from .equihash import EquihashAlgo
from .ethash import EtHashAlgo
from .handshake import HandshakeAlgo
from .hashrate import *
from .hashrate.unit import *
from .kadena import KadenaAlgo
from .kheavyhash import KHeavyHashAlgo
from .scrypt import ScryptAlgo
from .sha256 import SHA256Algo
from .x11 import X11Algo
from .zksnark import ZkSnarkAlgo


class MinerAlgo:
    SHA256 = SHA256Algo
    SCRYPT = ScryptAlgo
    KHEAVYHASH = KHeavyHashAlgo
    KADENA = KadenaAlgo
    HANDSHAKE = HandshakeAlgo
    X11 = X11Algo
    BLAKE256 = Blake256Algo
    EAGLESONG = EaglesongAlgo
    ETHASH = EtHashAlgo
    EQUIHASH = EquihashAlgo
    BLOCKFLOW = BlockFlowAlgo
    ZKSNARK = ZkSnarkAlgo
