# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

from pyasic.device.firmware import MinerFirmware
from pyasic.miners.base import BaseMiner


class StockFirmware(BaseMiner):
    firmware = MinerFirmware.STOCK

    async def upgrade_firmware(self, *, url: str = None, version: str = "latest") -> bool:
        return await super().upgrade_firmware(url=url, version=version)


class BraiinsOSFirmware(BaseMiner):
    firmware = MinerFirmware.BRAIINS_OS

    async def upgrade_firmware(self, *, url: str = None, version: str = "latest") -> bool:
        return await super().upgrade_firmware(url=url, version=version)


class VNishFirmware(BaseMiner):
    firmware = MinerFirmware.VNISH

    async def upgrade_firmware(self, *, url: str = None, version: str = "latest") -> bool:
        return await super().upgrade_firmware(url=url, version=version)


class ePICFirmware(BaseMiner):
    firmware = MinerFirmware.EPIC

    async def upgrade_firmware(self, *, url: str = None, version: str = "latest") -> bool:
        return await super().upgrade_firmware(url=url, version=version)


class HiveonFirmware(BaseMiner):
    firmware = MinerFirmware.HIVEON

    async def upgrade_firmware(self, *, url: str = None, version: str = "latest") -> bool:
        return await super().upgrade_firmware(url=url, version=version)


class LuxOSFirmware(BaseMiner):
    firmware = MinerFirmware.LUXOS

    async def upgrade_firmware(self, *, url: str = None, version: str = "latest") -> bool:
        return await super().upgrade_firmware(url=url, version=version)


class MaraFirmware(BaseMiner):
    firmware = MinerFirmware.MARATHON

    async def upgrade_firmware(self, *, url: str = None, version: str = "latest") -> bool:
        return await super().upgrade_firmware(url=url, version=version)
