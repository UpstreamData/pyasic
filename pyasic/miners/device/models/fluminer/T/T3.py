"""Fluminer T3 model metadata."""

from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import FluminerMake


class T3(FluminerMake):
    raw_model = MinerModel.FLUMINER.T3

    expected_hashboards = 1
    expected_chips = 96
    expected_fans = 4
    algo = MinerAlgo.SHA256
