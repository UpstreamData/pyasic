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
import logging
from enum import Enum

from pyasic import APIError, MinerConfig
from pyasic.miners.base import BaseMiner, DataLocations
from pyasic.rpc.gcminer import GCMinerRPCAPI
from pyasic.web.auradine import FluxWebAPI

AURADINE_DATA_LOC = DataLocations(**{})


class AuradineLEDColors(Enum):
    OFF = 0
    GREEN = 1
    RED = 2
    YELLOW = 3
    GREEN_FLASHING = 4
    RED_FLASHING = 5
    YELLOW_FLASHING = 6

    def __int__(self):
        return self.value


class AuradineLEDCodes(Enum):
    NO_POWER = 1
    NORMAL = 2
    LOCATE_MINER = 3
    TEMPERATURE = 4
    POOL_CONFIG = 5
    NETWORK = 6
    CONTROL_BOARD = 7
    HASH_RATE_LOW = 8
    CUSTOM1 = 101
    CUSTOM2 = 102

    def __int__(self):
        return self.value


class Auradine(BaseMiner):
    """Base handler for Auradine miners"""

    _api_cls = GCMinerRPCAPI
    api: GCMinerRPCAPI
    _web_cls = FluxWebAPI
    web: FluxWebAPI

    data_locations = AURADINE_DATA_LOC

    supports_shutdown = True
    supports_autotuning = True

    async def fault_light_on(self) -> bool:
        return await self.web.set_led(code=int(AuradineLEDCodes.LOCATE_MINER))

    async def fault_light_off(self) -> bool:
        return await self.web.set_led(code=int(AuradineLEDCodes.NORMAL))

    async def reboot(self) -> bool:
        try:
            await self.web.reboot()
        except APIError:
            return False
        return True

    async def restart_backend(self) -> bool:
        try:
            await self.web.restart_gcminer()
        except APIError:
            return False
        return True

    async def stop_mining(self) -> bool:
        try:
            await self.web.set_mode(sleep="on")
        except APIError:
            return False
        return True

    async def resume_mining(self) -> bool:
        try:
            await self.web.set_mode(sleep="off")
        except APIError:
            return False
        return True

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            await self.web.set_mode(mode="custom", tune="power", power=wattage)
        except APIError:
            return False
        return True

    async def get_config(self) -> MinerConfig:
        try:
            web_conf = await self.web.multicommand("pools", "mode", "fan")
            return MinerConfig.from_auradine(web_conf=web_conf)
        except APIError as e:
            logging.warning(e)
        except LookupError:
            pass
        return MinerConfig()

    async def send_config(self, config: MinerConfig, user_suffix: str = None) -> None:
        self.config = config

        conf = config.as_auradine(user_suffix=user_suffix)
        for key in conf.keys():
            await self.web.send_command(command=key, **conf[key])

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################
