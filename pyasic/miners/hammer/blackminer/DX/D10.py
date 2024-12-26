from pyasic.miners.backends import BlackMiner
from pyasic.miners.device.models import D10


class HammerD10(BlackMiner, D10):
    sticker_hashrate = 5000
