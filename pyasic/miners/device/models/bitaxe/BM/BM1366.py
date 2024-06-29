from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import BitAxeMake


class Ultra(BitAxeMake):
    raw_model = MinerModel.BITAXE.BM1366

    expected_hashboards = 1
    expected_chips = 1
    expected_fans = 1
