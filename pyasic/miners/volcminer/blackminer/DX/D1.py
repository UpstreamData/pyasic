from pyasic.miners.backends import BlackMiner
from pyasic.miners.device.models import D1
from pyasic.device.algorithm.scrypt import ScryptHashRate
from pyasic.device.algorithm.hashrate.unit.scrypt import ScryptUnit


class VolcMinerD1(BlackMiner, D1):
    sticker_hashrate = ScryptHashRate(rate=15.15, unit=ScryptUnit.GH)
