from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M70VM30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M70VM30

    expected_chips = 147
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
