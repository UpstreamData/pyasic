from pydantic import BaseModel, ConfigDict

from pyasic.device.algorithm import MinerAlgoType
from pyasic.device.firmware import MinerFirmware
from pyasic.device.makes import MinerMake
from pyasic.device.models import MinerModelType


class DeviceInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    make: MinerMake | None = None
    model: MinerModelType | None = None
    firmware: MinerFirmware | None = None
    algo: MinerAlgoType | None = None
