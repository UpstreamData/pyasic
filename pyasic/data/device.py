from dataclasses import dataclass

from pyasic.device.algorithm import MinerAlgo
from pyasic.device.firmware import MinerFirmware
from pyasic.device.makes import MinerMake
from pyasic.device.models import MinerModel


@dataclass
class DeviceInfo:
    make: MinerMake = None
    model: MinerModel = None
    firmware: MinerFirmware = None
    algo: MinerAlgo = None
