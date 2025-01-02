from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M30LV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M30LV10

    expected_chips = 144
    expected_fans = 2
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
