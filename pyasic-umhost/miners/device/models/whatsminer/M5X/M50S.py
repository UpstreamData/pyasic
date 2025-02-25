from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M50SVH10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH10

    expected_chips = None
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH20

    expected_chips = 135
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH30

    expected_chips = 156
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH40

    expected_chips = 148
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVH50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVH50

    expected_chips = 135
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVJ10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVJ10

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVJ20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVJ20

    expected_chips = 117
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVJ30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVJ30

    expected_chips = 123
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVJ40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVJ40

    expected_chips = 129
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVJ50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVJ50

    expected_chips = 135
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVK10

    expected_chips = 78
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVK20

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVK30

    expected_chips = 117
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVK50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVK50

    expected_chips = 105
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVK60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVK60

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVK70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVK70

    expected_chips = 123
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVK80(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVK80

    expected_chips = 86
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVL20

    expected_chips = 78
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M50SVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M50SVL30

    expected_chips = 82
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
