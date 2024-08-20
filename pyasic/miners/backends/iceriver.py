from pyasic.miners.data import DataLocations
from pyasic.miners.device.firmware import StockFirmware
from pyasic.web.iceriver import IceRiverWebAPI

ICERIVER_DATA_LOC = DataLocations()


class IceRiver(StockFirmware):
    """Handler for IceRiver miners"""

    _web_cls = IceRiverWebAPI
    web: IceRiverWebAPI

    data_locations = ICERIVER_DATA_LOC
