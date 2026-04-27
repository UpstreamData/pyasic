from pyasic.miners.backends import M6X
from pyasic.miners.device.models import (
    M60SPlusPlusVLA0,
    M60SPlusPlusVL30,
    M60SPlusPlusVL40,
    M60SPlusPlusVL80,
    M60SPlusPlusVLB0,
)


class BTMinerM60SPlusPlusVLA0(M6X, M60SPlusPlusVLA0):
    pass


class BTMinerM60SPlusPlusVLB0(M6X, M60SPlusPlusVLB0):
    pass


class BTMinerM60SPlusPlusVL30(M6X, M60SPlusPlusVL30):
    pass


from pyasic.miners.device.models import M60SPlusPlusVL40


class BTMinerM60SPlusPlusVL40(M6X, M60SPlusPlusVL40):
    pass


class BTMinerM60SPlusPlusVL80(M6X, M60SPlusPlusVL80):
    pass