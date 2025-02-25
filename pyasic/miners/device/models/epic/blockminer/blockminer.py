from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import ePICMake


class BlockMiner520i(ePICMake):
    raw_model = MinerModel.EPIC.BM520i

    expected_chips = 124
    expected_fans = 4
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class BlockMiner720i(ePICMake):
    raw_model = MinerModel.EPIC.BM720i

    expected_chips = 180
    expected_fans = 4
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
