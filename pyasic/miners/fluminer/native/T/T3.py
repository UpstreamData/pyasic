"""Fluminer T3 native firmware miner class."""

from pyasic.miners.backends.fluminer import Fluminer
from pyasic.miners.device.models.fluminer import T3


class FluminerT3(Fluminer, T3):
    pass
