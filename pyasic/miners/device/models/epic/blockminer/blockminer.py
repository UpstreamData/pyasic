from pyasic.device.models import MinerModels
from pyasic.miners.device.makes import ePICMake


class BlockMiner520i(ePICMake):
    raw_model = MinerModels.EPIC.BM520i

    expected_chips = 124
    expected_fans = 4


class BlockMiner720i(ePICMake):
    raw_model = MinerModels.EPIC.BM720i

    expected_chips = 180
    expected_fans = 4
