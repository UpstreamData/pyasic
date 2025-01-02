from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M31SEV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SEV10

    expected_chips = 82
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SEV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SEV20

    expected_chips = 78
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SEV30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SEV30

    expected_chips = 78
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
