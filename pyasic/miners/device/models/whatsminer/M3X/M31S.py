from pyasic.device.algorithm import MinerAlgo
from pyasic.device.models import MinerModel
from pyasic.miners.device.makes import WhatsMinerMake


class M31SV10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV10

    expected_chips = 105
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SV20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV20

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SV30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV30

    expected_chips = 117
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SV40(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV40

    expected_chips = 123
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SV50(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV50

    expected_chips = 78
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SV60(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV60

    expected_chips = 105
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SV70(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV70

    expected_chips = 111
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SV80(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV80

    expected_chips = None
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SV90(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SV90

    expected_chips = 117
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SVE10(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SVE10

    expected_chips = 70
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SVE20(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SVE20

    expected_chips = 74
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256


class M31SVE30(WhatsMinerMake):
    raw_model = MinerModel.WHATSMINER.M31SVE30

    expected_chips = None
    expected_fans = 2
    expected_hashboards = 3
    algo = MinerAlgo.SHA256
