from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M60SPlusVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVK30

    expected_chips = 245
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SPlusVK40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVK40

    expected_chips = 215
    expected_fans = 2
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M60SPlusVK50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVK50

    expected_chips = 225
    expected_fans = 2
    expected_hashboards = 4
    algo = MinerAlgo.SHA256


class M60SPlusVK60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVK60

    expected_chips = 294
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SPlusVK70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVK70

    expected_chips = 306
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SPlusVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVL10

    expected_chips = 196
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SPlusVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVL30

    expected_chips = 225
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SPlusVL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVL40

    expected_chips = 188
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SPlusVL50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVL50

    expected_chips = 180
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SPlusVL60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SPlusVL60

    expected_chips = 172
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
