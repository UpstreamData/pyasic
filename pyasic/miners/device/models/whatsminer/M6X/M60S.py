from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M60SVK10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVK10

    expected_chips = 215
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVK20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVK20

    expected_chips = 235
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVK30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVK30

    expected_chips = 245
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVK40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVK40

    expected_chips = 225
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVL10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVL10

    expected_chips = 147
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVL20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVL20

    expected_chips = 164
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVL30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVL30

    expected_chips = 172
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVL40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVL40

    expected_chips = 180
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVL50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVL50

    expected_chips = 188
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVL60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVL60

    expected_chips = 196
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M60SVL70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M60SVL70

    expected_chips = 141
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
