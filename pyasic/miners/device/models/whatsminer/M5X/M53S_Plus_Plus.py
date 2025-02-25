from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M53SPlusPlusVK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusPlusVK10

    expected_chips = 198
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SPlusPlusVK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusPlusVK20

    expected_chips = 192
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SPlusPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusPlusVK30

    expected_chips = 240
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SPlusPlusVK50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusPlusVK50

    expected_chips = 186
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SPlusPlusVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusPlusVL10

    expected_chips = 128
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M53SPlusPlusVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M53SPlusPlusVL30

    expected_chips = 174
    expected_fans = 0
    expected_hashboards = 4
    algo = MinerAlgo.SHA256
