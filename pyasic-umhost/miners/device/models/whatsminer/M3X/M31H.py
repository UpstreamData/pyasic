from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M31HV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31HV10

    expected_chips = 114
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31HV40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31HV40

    expected_chips = 136
    expected_fans = 2
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
