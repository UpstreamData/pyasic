from pydantic import BaseModel, ConfigDict, field_serializer

from pyasic.device.algorithm import MinerAlgoType
from pyasic.device.firmware import MinerFirmware
from pyasic.device.makes import MinerMake
from pyasic.device.models import MinerModelType


class DeviceInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    make: MinerMake | None = None
    model: MinerModelType | None = None
    firmware: MinerFirmware | None = None
    algo: type[MinerAlgoType] | None = None

    @field_serializer("make")
    def serialize_make(self, make: MinerMake, _info):
        return str(make)

    @field_serializer("model")
    def serialize_model(self, model: MinerModelType, _info):
        return str(model)

    @field_serializer("firmware")
    def serialize_firmware(self, firmware: MinerFirmware, _info):
        return str(firmware)

    @field_serializer("algo")
    def serialize_algo(self, algo: MinerAlgoType, _info):
        return str(algo)
