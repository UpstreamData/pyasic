from pyasic.miners.backends import M3X
from pyasic.miners.device.models import M30V10


class BTMinerM30V10(M3X, M30V10):
    pass


from pyasic.miners.device.models import M30V20


class BTMinerM30V20(M3X, M30V20):
    pass
