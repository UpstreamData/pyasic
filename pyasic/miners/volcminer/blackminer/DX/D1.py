from pyasic.miners.backends import BlackMiner
from pyasic.miners.device.models import D1


class VolcMinerD1(BlackMiner, D1):
    sticker_hashrate = 15150000
