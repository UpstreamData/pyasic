from dataclasses import dataclass

from pyasic.device.firmware import MinerFirmware
from pyasic.device.makes import MinerMake


@dataclass
class DeviceInfo:
    make: MinerMake = None
    model: str = None
    firmware: MinerFirmware = None
