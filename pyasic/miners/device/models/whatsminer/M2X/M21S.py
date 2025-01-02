from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M21SV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M21SV20

    expected_chips = 66
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M21SV60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M21SV60

    expected_chips = 105
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M21SV70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M21SV70

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
