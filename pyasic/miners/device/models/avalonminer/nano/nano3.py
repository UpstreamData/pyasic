from pyasic.device import MinerModel
from pyasic.miners.device.makes import AvalonMinerMake


class AvalonNano3(AvalonMinerMake):
    raw_model = MinerModel.AVALONMINER.AvalonNano3

    expected_hashboards = 1
    expected_chips = 10
    expected_fans = 1
