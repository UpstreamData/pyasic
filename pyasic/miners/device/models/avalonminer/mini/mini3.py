from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import AvalonMinerMake


class AvalonMini3(AvalonMinerMake):
    raw_model = MinerModel.AVALONMINER.AvalonMini3

    expected_hashboards = 1
    expected_chips = 66
    expected_fans = 1
    algo = MinerAlgo.SHA256
