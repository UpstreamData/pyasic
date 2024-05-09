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
from typing import List, Optional

from pyasic.config import MinerConfig
from pyasic.data import AlgoHashRate, Fan, HashBoard, HashUnit
from pyasic.errors import APIError
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.firmware import StockFirmware
from pyasic.rpc.gcminer import GCMinerRPCAPI
from pyasic.web.auradine import AuradineWebAPI

AURADINE_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_ipreport", "ipreport")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_ipreport", "ipreport")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_ipreport", "ipreport")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [
                RPCAPICommand("rpc_devs", "devs"),
                WebAPICommand("web_ipreport", "ipreport"),
            ],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_psu", "psu")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [WebAPICommand("web_mode", "mode"), WebAPICommand("web_psu", "psu")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_fan", "fan")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("web_led", "led")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [WebAPICommand("web_mode", "mode")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
    }
)


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


class Auradine(StockFirmware):
    """Base handler for Auradine miners"""

    _rpc_cls = GCMinerRPCAPI
    rpc: GCMinerRPCAPI
    _web_cls = AuradineWebAPI
    web: AuradineWebAPI

    data_locations = AURADINE_DATA_LOC

    supports_shutdown = True
    supports_power_modes = True
    supports_autotuning = True

    async def fault_light_on(self) -> bool:
        try:
            await self.web.set_led(code=int(AuradineLEDCodes.LOCATE_MINER))
            return True
        except APIError:
            return False

    async def fault_light_off(self) -> bool:
        try:
            await self.web.set_led(code=int(AuradineLEDCodes.NORMAL))
            return True
        except APIError:
            return False

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

    async def _get_mac(self, web_ipreport: dict = None) -> Optional[str]:
        if web_ipreport is None:
            try:
                web_ipreport = await self.web.ipreport()
            except APIError:
                pass

        if web_ipreport is not None:
            try:
                return web_ipreport["IPReport"][0]["mac"].upper()
            except (LookupError, AttributeError):
                pass

    async def _get_fw_ver(self, web_ipreport: dict = None) -> Optional[str]:
        if web_ipreport is None:
            try:
                web_ipreport = await self.web.ipreport()
            except APIError:
                pass

        if web_ipreport is not None:
            try:
                return web_ipreport["IPReport"][0]["version"]
            except LookupError:
                pass

    async def _get_hostname(self, web_ipreport: dict = None) -> Optional[str]:
        if web_ipreport is None:
            try:
                web_ipreport = await self.web.ipreport()
            except APIError:
                pass

        if web_ipreport is not None:
            try:
                return web_ipreport["IPReport"][0]["hostname"]
            except LookupError:
                pass

    async def _get_hashrate(self, rpc_summary: dict = None) -> Optional[float]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return AlgoHashRate.SHA256(
                    rpc_summary["SUMMARY"][0]["MHS 5s"], HashUnit.SHA256.MH
                ).into(self.algo.unit.default)
            except (LookupError, ValueError, TypeError):
                pass

    async def _get_hashboards(
        self, rpc_devs: dict = None, web_ipreport: dict = None
    ) -> List[HashBoard]:
        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                pass
        if web_ipreport is None:
            try:
                web_ipreport = await self.web.ipreport()
            except APIError:
                pass

        if rpc_devs is not None:
            try:
                for board in rpc_devs["DEVS"]:
                    b_id = board["ID"] - 1
                    hashboards[b_id].hashrate = AlgoHashRate.SHA256(
                        board["MHS 5s"], HashUnit.SHA256.MH
                    ).into(self.algo.unit.default)
                    hashboards[b_id].temp = round(float(float(board["Temperature"])), 2)
                    hashboards[b_id].missing = False
            except LookupError:
                pass

        if web_ipreport is not None:
            try:
                for board, sn in enumerate(web_ipreport["IPReport"][0]["HBSerialNo"]):
                    hashboards[board].serial_number = sn
                    hashboards[board].missing = False
            except LookupError:
                pass

        return hashboards

    async def _get_wattage(self, web_psu: dict = None) -> Optional[int]:
        if web_psu is None:
            try:
                web_psu = await self.web.get_psu()
            except APIError:
                pass

        if web_psu is not None:
            try:
                return int(float(web_psu["PSU"][0]["PowerIn"].replace("W", "")))
            except (LookupError, TypeError, ValueError):
                pass

    async def _get_wattage_limit(
        self, web_mode: dict = None, web_psu: dict = None
    ) -> Optional[int]:
        if web_mode is None:
            try:
                web_mode = await self.web.get_mode()
            except APIError:
                pass

        if web_mode is not None:
            try:
                return web_mode["Mode"][0]["Power"]
            except (LookupError, TypeError, ValueError):
                pass

        if web_psu is None:
            try:
                web_psu = await self.web.get_psu()
            except APIError:
                pass

        if web_psu is not None:
            try:
                return int(float(web_psu["PSU"][0]["PoutMax"].replace("W", "")))
            except (LookupError, TypeError, ValueError):
                pass

    async def _get_fans(self, web_fan: dict = None) -> List[Fan]:
        if web_fan is None:
            try:
                web_fan = await self.web.get_fan()
            except APIError:
                pass

        fans = []
        if web_fan is not None:
            try:
                for fan in web_fan["Fan"]:
                    fans.append(Fan(round(fan["Speed"])))
            except LookupError:
                pass
        return fans

    async def _get_fault_light(self, web_led: dict = None) -> Optional[bool]:
        if web_led is None:
            try:
                web_led = await self.web.get_led()
            except APIError:
                pass

        if web_led is not None:
            try:
                return web_led["LED"][0]["Code"] == int(AuradineLEDCodes.LOCATE_MINER)
            except LookupError:
                pass

    async def _is_mining(self, web_mode: dict = None) -> Optional[bool]:
        if web_mode is None:
            try:
                web_mode = await self.web.get_mode()
            except APIError:
                pass

        if web_mode is not None:
            try:
                return web_mode["Mode"][0]["Sleep"] == "off"
            except (LookupError, TypeError, ValueError):
                pass

    async def _get_uptime(self, rpc_summary: dict = None) -> Optional[int]:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                pass

        if rpc_summary is not None:
            try:
                return rpc_summary["SUMMARY"][0]["Elapsed"]
            except LookupError:
                pass
