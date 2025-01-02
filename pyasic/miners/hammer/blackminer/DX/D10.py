from pyasic.miners.backends import BlackMiner
from pyasic.miners.device.models import D10
from pyasic.device.algorithm.scrypt import ScryptHashRate
from pyasic.device.algorithm.hashrate.unit.scrypt import ScryptUnit


class HammerD10(BlackMiner, D10):
    sticker_hashrate = ScryptHashRate(rate=5.0, unit=ScryptUnit.GH)
