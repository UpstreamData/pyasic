from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M20SV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M20SV10

    expected_chips = 105
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M20SV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M20SV20

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M20SV30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M20SV30

    expected_chips = 140
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
