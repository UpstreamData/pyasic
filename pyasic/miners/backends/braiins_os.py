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
import base64
import logging
import time
from typing import Any

import aiofiles
import tomli_w
from pydantic import BaseModel, Field, ValidationError

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from pyasic.config import MinerConfig
from pyasic.config.mining import MiningModePowerTune
from pyasic.data.boards import HashBoard
from pyasic.data.error_codes import BraiinsOSError, MinerErrorData
from pyasic.data.fans import Fan
from pyasic.data.pools import PoolMetrics, PoolUrl
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.data import (
    DataFunction,
    DataLocations,
    DataOptions,
    RPCAPICommand,
    WebAPICommand,
)
from pyasic.miners.device.firmware import BraiinsOSFirmware
from pyasic.rpc.bosminer import BOSMinerRPCAPI
from pyasic.ssh.braiins_os import BOSMinerSSH
from pyasic.web.braiins_os import BOSerWebAPI, BOSMinerWebAPI
from pyasic.web.braiins_os.proto.braiins.bos.v1 import SaveAction


class BOSNetworkInterfaceStatus(BaseModel):
    macaddr: str | None = None

    class Config:
        extra = "allow"


class BOSInfoResponse(BaseModel):
    version: str | None = None

    class Config:
        extra = "allow"


class BOSVersionResponse(BaseModel):
    api: str | None = Field(None, alias="API")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSVersionWrapper(BaseModel):
    version: list[BOSVersionResponse] = Field([], alias="VERSION")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSSummaryItem(BaseModel):
    mhs_1m: float | None = Field(None, alias="MHS 1m")
    elapsed: int | None = Field(None, alias="Elapsed")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSSummaryWrapper(BaseModel):
    summary: list[BOSSummaryItem] = Field([], alias="SUMMARY")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSTempItem(BaseModel):
    id: int = Field(alias="ID")
    chip: float | None = Field(None, alias="Chip")
    board: float | None = Field(None, alias="Board")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSTempsWrapper(BaseModel):
    temps: list[BOSTempItem] = Field([], alias="TEMPS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSDevDetailsItem(BaseModel):
    id: int = Field(alias="ID")
    chips: int | None = Field(None, alias="Chips")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSDevDetailsWrapper(BaseModel):
    devdetails: list[BOSDevDetailsItem] = Field([], alias="DEVDETAILS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSDevsItem(BaseModel):
    id: int = Field(alias="ID")
    mhs_1m: float | None = Field(None, alias="MHS 1m")
    nominal_mhs: float | None = Field(None, alias="Nominal MHS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSDevsWrapper(BaseModel):
    devs: list[BOSDevsItem] = Field([], alias="DEVS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSTunerChainStatus(BaseModel):
    hashchain_index: int = Field(alias="HashchainIndex")
    status: str | None = Field(None, alias="Status")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSTunerStatusItem(BaseModel):
    approximate_miner_power_consumption: float | None = Field(
        None, alias="ApproximateMinerPowerConsumption"
    )
    power_limit: int | None = Field(None, alias="PowerLimit")
    tuner_chain_status: list[BOSTunerChainStatus] | None = Field(
        None, alias="TunerChainStatus"
    )

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSTunerStatusWrapper(BaseModel):
    tunerstatus: list[BOSTunerStatusItem] = Field([], alias="TUNERSTATUS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSFanItem(BaseModel):
    rpm: int | None = Field(None, alias="RPM")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSFansWrapper(BaseModel):
    fans: list[BOSFanItem] = Field([], alias="FANS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSStatusItem(BaseModel):
    msg: str | None = Field(None, alias="Msg")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSStatusWrapper(BaseModel):
    status: list[BOSStatusItem] = Field([], alias="STATUS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSPoolItem(BaseModel):
    pool: int | None = Field(None, alias="POOL")
    url: str | None = Field(None, alias="URL")
    user: str | None = Field(None, alias="User")
    accepted: int | None = Field(None, alias="Accepted")
    rejected: int | None = Field(None, alias="Rejected")
    get_failures: int | None = Field(None, alias="Get Failures")
    remote_failures: int | None = Field(None, alias="Remote Failures")
    stratum_active: bool | None = Field(None, alias="Stratum Active")
    status: str | None = Field(None, alias="Status")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSPoolsWrapper(BaseModel):
    pools: list[BOSPoolItem] = Field([], alias="POOLS")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerBosVersion(BaseModel):
    current: str | None = None

    class Config:
        extra = "allow"


class BOSerHashrateInfo(BaseModel):
    gigahashPerSecond: float | None = None

    class Config:
        extra = "allow"


class BOSerMinerDetails(BaseModel):
    mac_address: str | None = Field(None, alias="macAddress")
    hostname: str | None = None
    bos_version: BOSerBosVersion | None = Field(None, alias="bosVersion")
    sticker_hashrate: BOSerHashrateInfo | None = Field(None, alias="stickerHashrate")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerHashBoardStats(BaseModel):
    real_hashrate: dict[str, BOSerHashrateInfo] | None = Field(
        None, alias="realHashrate"
    )

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerTemperature(BaseModel):
    degree_c: float | None = Field(None, alias="degreeC")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerChipTemp(BaseModel):
    temperature: BOSerTemperature | None = None

    class Config:
        extra = "allow"


class BOSerHashBoard(BaseModel):
    id: str | None = None
    chips_count: int | None = Field(None, alias="chipsCount")
    board_temp: BOSerTemperature | None = Field(None, alias="boardTemp")
    highest_chip_temp: BOSerChipTemp | None = Field(None, alias="highestChipTemp")
    stats: BOSerHashBoardStats | None = None

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerHashBoards(BaseModel):
    hashboards: list[BOSerHashBoard] = []

    class Config:
        extra = "allow"


class BOSerPowerTarget(BaseModel):
    watt: int | None = None

    class Config:
        extra = "allow"


class BOSerPowerStats(BaseModel):
    approximated_consumption: BOSerPowerTarget | None = Field(
        None, alias="approximatedConsumption"
    )

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerMinerStats(BaseModel):
    power_stats: BOSerPowerStats | None = Field(None, alias="powerStats")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerTunerMode(BaseModel):
    power_target: dict[str, BOSerPowerTarget] | None = Field(None, alias="powerTarget")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerActivePerformanceMode(BaseModel):
    tuner_mode: BOSerTunerMode | None = Field(None, alias="tunerMode")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerFan(BaseModel):
    rpm: int | None = None

    class Config:
        extra = "allow"


class BOSerCoolingState(BaseModel):
    fans: list[BOSerFan] = []

    class Config:
        extra = "allow"


class BOSerPoolStats(BaseModel):
    accepted_shares: int = Field(0, alias="acceptedShares")
    rejected_shares: int = Field(0, alias="rejectedShares")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerPool(BaseModel):
    url: str | None = None
    user: str | None = None
    active: bool = False
    alive: bool | None = None
    stats: BOSerPoolStats | None = None

    class Config:
        extra = "allow"


class BOSerPoolGroup(BaseModel):
    pools: list[BOSerPool] = []

    class Config:
        extra = "allow"


class BOSerPoolGroups(BaseModel):
    pool_groups: list[BOSerPoolGroup] = Field([], alias="poolGroups")

    class Config:
        populate_by_name = True
        extra = "allow"


class BOSerLocateDeviceStatus(BaseModel):
    enabled: bool | None = None

    class Config:
        extra = "allow"


BOSMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_net_conf", "admin/network/iface_status/lan")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_bos_info", "bos/info")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [RPCAPICommand("rpc_devs", "devs")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [
                RPCAPICommand("rpc_temps", "temps"),
                RPCAPICommand("rpc_devdetails", "devdetails"),
                RPCAPICommand("rpc_devs", "devs"),
            ],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [RPCAPICommand("rpc_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [RPCAPICommand("rpc_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [RPCAPICommand("rpc_fans", "fans")],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [RPCAPICommand("rpc_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [RPCAPICommand("rpc_devdetails", "devdetails")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools",
            [RPCAPICommand("rpc_pools", "pools")],
        ),
    }
)


class BOSMiner(BraiinsOSFirmware):
    """Handler for old versions of BraiinsOS+ (pre-gRPC)"""

    _rpc_cls = BOSMinerRPCAPI
    rpc: BOSMinerRPCAPI
    _web_cls = BOSMinerWebAPI
    web: BOSMinerWebAPI
    _ssh_cls = BOSMinerSSH
    ssh: BOSMinerSSH

    data_locations = BOSMINER_DATA_LOC

    supports_shutdown = True
    supports_autotuning = True

    async def fault_light_on(self) -> bool:
        ret = await self.ssh.fault_light_on()

        if isinstance(ret, str):
            self.light = True
            return self.light
        return False

    async def fault_light_off(self) -> bool:
        ret = await self.ssh.fault_light_off()

        if isinstance(ret, str):
            self.light = False
            return True
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_bosminer()

    async def restart_bosminer(self) -> bool:
        ret = await self.ssh.restart_bosminer()

        if isinstance(ret, str):
            return True
        return False

    async def stop_mining(self) -> bool:
        try:
            data = await self.rpc.pause()
        except APIError:
            return False

        if data.get("PAUSE"):
            if data["PAUSE"][0]:
                return True
        return False

    async def resume_mining(self) -> bool:
        try:
            data = await self.rpc.resume()
        except APIError:
            return False

        if data.get("RESUME"):
            if data["RESUME"][0]:
                return True
        return False

    async def reboot(self) -> bool:
        ret = await self.ssh.reboot()

        if isinstance(ret, str):
            return True
        return False

    async def get_config(self) -> MinerConfig:
        raw_data = await self.ssh.get_config_file()

        if raw_data is None:
            raise APIError("Failed to get config file.")

        try:
            toml_data = tomllib.loads(raw_data)
            cfg = MinerConfig.from_bosminer(toml_data)
            self.config = cfg
        except tomllib.TOMLDecodeError as e:
            raise APIError("Failed to decode toml when getting config.") from e
        except TypeError as e:
            raise APIError("Failed to decode toml when getting config.") from e

        return self.config

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        self.config = config
        parsed_cfg = config.as_bosminer(user_suffix=user_suffix)

        toml_conf = tomli_w.dumps(
            {
                "format": {
                    "version": "2.0",
                    "generator": "pyasic",
                    "model": f"{self.make.replace('Miner', 'miner') if self.make else ''} {self.raw_model.replace('j', 'J') if self.raw_model else ''}",
                    "timestamp": int(time.time()),
                },
                **parsed_cfg,
            }
        )
        try:
            await self.ssh.send_command("/etc/init.d/bosminer stop")
            await self.ssh.send_command("echo '" + toml_conf + "' > /etc/bosminer.toml")
            await self.ssh.send_command("/etc/init.d/bosminer start")
        except Exception as e:
            raise APIError("SSH command failed when sending config.") from e

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            cfg = await self.get_config()
            if cfg is None:
                return False
            cfg.mining_mode = MiningModePowerTune(power=wattage)
            await self.send_config(cfg)
        except APIError:
            raise
        except Exception as e:
            logging.warning(f"{self} - Failed to set power limit: {e}")
            return False
        else:
            return True

    async def set_static_ip(
        self,
        ip: str,
        dns: str,
        gateway: str,
        subnet_mask: str = "255.255.255.0",
    ) -> None:
        cfg_data_lan = "\n\t".join(
            [
                "config interface 'lan'",
                "option type 'bridge'",
                "option ifname 'eth0'",
                "option proto 'static'",
                f"option ipaddr '{ip}'",
                f"option netmask '{subnet_mask}'",
                f"option gateway '{gateway}'",
                f"option dns '{dns}'",
            ]
        )
        data = await self.ssh.get_network_config()

        if data is None:
            raise APIError("Failed to get network config.")

        split_data = data.split("\n\n")
        for idx, val in enumerate(split_data):
            if "config interface 'lan'" in val:
                split_data[idx] = cfg_data_lan
        config = "\n\n".join(split_data)

        await self.ssh.send_command("echo '" + config + "' > /etc/config/network")

    async def set_dhcp(self) -> None:
        cfg_data_lan = "\n\t".join(
            [
                "config interface 'lan'",
                "option type 'bridge'",
                "option ifname 'eth0'",
                "option proto 'dhcp'",
            ]
        )
        data = await self.ssh.get_network_config()

        if data is None:
            raise APIError("Failed to get network config.")

        split_data = data.split("\n\n")
        for idx, val in enumerate(split_data):
            if "config interface 'lan'" in val:
                split_data[idx] = cfg_data_lan
        config = "\n\n".join(split_data)

        await self.ssh.send_command("echo '" + config + "' > /etc/config/network")

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(
        self, web_net_conf: dict[str, Any] | list[Any] | None = None
    ) -> str | None:
        if web_net_conf is None:
            try:
                web_net_conf = await self.web.get_net_conf()
            except APIError:
                return None

        if isinstance(web_net_conf, dict):
            if "admin/network/iface_status/lan" in web_net_conf.keys():
                web_net_conf = web_net_conf["admin/network/iface_status/lan"]

        if web_net_conf is not None:
            try:
                if isinstance(web_net_conf, list) and len(web_net_conf) > 0:
                    response = BOSNetworkInterfaceStatus.model_validate(web_net_conf[0])
                elif isinstance(web_net_conf, dict):
                    response = BOSNetworkInterfaceStatus.model_validate(web_net_conf)
                else:
                    return None

                if response.macaddr:
                    return response.macaddr
            except ValidationError as e:
                logging.warning(f"{self} - Failed to parse network config for MAC: {e}")
        return None
        # could use ssh, but its slow and buggy
        # result = await self.send_ssh_command("cat /sys/class/net/eth0/address")
        # if result:
        #     return result.upper().strip()

    async def _get_api_ver(
        self, rpc_version: dict[str, Any] | None = None
    ) -> str | None:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                return None

        if rpc_version is not None:
            try:
                response = BOSVersionWrapper.model_validate(rpc_version)
                if response.version and response.version[0].api:
                    self.api_ver = response.version[0].api
                    self.rpc.rpc_ver = self.api_ver  # type: ignore
                    return self.api_ver
            except ValidationError as e:
                logging.warning(f"{self} - Failed to parse version for API: {e}")

        return self.api_ver

    async def _get_fw_ver(
        self, web_bos_info: dict[str, Any] | None = None
    ) -> str | None:
        if web_bos_info is None:
            try:
                web_bos_info = await self.web.get_bos_info()
            except APIError:
                return None

        if web_bos_info is None:
            return None

        if isinstance(web_bos_info, dict):
            if "bos/info" in web_bos_info.keys():
                web_bos_info = web_bos_info["bos/info"]

        try:
            response = BOSInfoResponse.model_validate(web_bos_info)
            if response.version:
                ver = response.version.split("-")[5]
                if "." in ver:
                    self.fw_ver = ver
                    return self.fw_ver
        except (ValidationError, AttributeError, IndexError) as e:
            if isinstance(e, ValidationError):
                logging.warning(f"{self} - Failed to parse BOS info for firmware: {e}")
            return None

        return self.fw_ver

    async def _get_hostname(self) -> str | None:
        try:
            hostname_result = await self.ssh.get_hostname()
            if hostname_result is not None:
                hostname = hostname_result.strip()
            else:
                return None
        except AttributeError:
            return None
        except Exception as e:
            logging.error(f"{self} - Getting hostname failed: {e}")
            return None
        return hostname

    async def _get_hashrate(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                return None

        if rpc_summary is not None:
            try:
                response = BOSSummaryWrapper.model_validate(rpc_summary)
                if response.summary and response.summary[0].mhs_1m is not None:
                    return self.algo.hashrate(
                        rate=float(response.summary[0].mhs_1m),
                        unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                    ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError as e:
                logging.warning(f"{self} - Failed to parse summary for hashrate: {e}")
        return None

    async def _get_hashboards(
        self,
        rpc_temps: dict[str, Any] | None = None,
        rpc_devdetails: dict[str, Any] | None = None,
        rpc_devs: dict[str, Any] | None = None,
    ) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        cmds = []
        if rpc_temps is None:
            cmds.append("temps")
        if rpc_devdetails is None:
            cmds.append("devdetails")
        if rpc_devs is None:
            cmds.append("devs")
        if len(cmds) > 0:
            try:
                d = await self.rpc.multicommand(*cmds)
            except APIError:
                d = {}
            try:
                rpc_temps = d["temps"][0]
            except LookupError:
                rpc_temps = None
            try:
                rpc_devdetails = d["devdetails"][0]
            except (KeyError, IndexError):
                rpc_devdetails = None
            try:
                rpc_devs = d["devs"][0]
            except LookupError:
                rpc_devs = None
        if rpc_temps is not None:
            try:
                temps_response = BOSTempsWrapper.model_validate(rpc_temps)
                if temps_response.temps:
                    offset = 6 if temps_response.temps[0].id in [6, 7, 8] else 1
                    for board in temps_response.temps:
                        if board.id is not None:
                            _id = board.id - offset
                            if 0 <= _id < len(hashboards):
                                if board.chip is not None:
                                    hashboards[_id].chip_temp = round(board.chip)
                                if board.board is not None:
                                    hashboards[_id].temp = round(board.board)
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse temps for hashboards: {e}")

        if rpc_devdetails is not None:
            try:
                devdetails_response = BOSDevDetailsWrapper.model_validate(
                    rpc_devdetails
                )
                if devdetails_response.devdetails:
                    offset = (
                        6 if devdetails_response.devdetails[0].id in [6, 7, 8] else 1
                    )
                    for dev_detail in devdetails_response.devdetails:
                        if dev_detail.id is not None:
                            _id = dev_detail.id - offset
                            if 0 <= _id < len(hashboards):
                                if dev_detail.chips is not None:
                                    hashboards[_id].chips = dev_detail.chips
                                hashboards[_id].missing = False
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse devdetails for hashboards: {e}"
                )

        if rpc_devs is not None:
            try:
                devs_response = BOSDevsWrapper.model_validate(rpc_devs)
                if devs_response.devs:
                    offset = 6 if devs_response.devs[0].id in [6, 7, 8] else 1
                    for dev_item in devs_response.devs:
                        if dev_item.id is not None and dev_item.mhs_1m is not None:
                            _id = dev_item.id - offset
                            if 0 <= _id < len(hashboards):
                                hashboards[_id].hashrate = self.algo.hashrate(
                                    rate=float(dev_item.mhs_1m),
                                    unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                                ).into(
                                    self.algo.unit.default  # type: ignore[attr-defined]
                                )
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse devs for hashboards: {e}")

        return hashboards

    async def _get_wattage(
        self, rpc_tunerstatus: dict[str, Any] | None = None
    ) -> int | None:
        if rpc_tunerstatus is None:
            try:
                rpc_tunerstatus = await self.rpc.tunerstatus()
            except APIError:
                return None

        if rpc_tunerstatus is not None:
            try:
                response = BOSTunerStatusWrapper.model_validate(rpc_tunerstatus)
                if (
                    response.tunerstatus
                    and response.tunerstatus[0].approximate_miner_power_consumption
                    is not None
                ):
                    return int(
                        response.tunerstatus[0].approximate_miner_power_consumption
                    )
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse tunerstatus for wattage: {e}")
        return None

    async def _get_wattage_limit(
        self, rpc_tunerstatus: dict[str, Any] | None = None
    ) -> int | None:
        if rpc_tunerstatus is None:
            try:
                rpc_tunerstatus = await self.rpc.tunerstatus()
            except APIError:
                return None

        if rpc_tunerstatus is not None:
            try:
                response = BOSTunerStatusWrapper.model_validate(rpc_tunerstatus)
                if (
                    response.tunerstatus
                    and response.tunerstatus[0].power_limit is not None
                ):
                    return int(response.tunerstatus[0].power_limit)
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse tunerstatus for wattage limit: {e}"
                )
        return None

    async def _get_fans(self, rpc_fans: dict[str, Any] | None = None) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if rpc_fans is None:
            try:
                rpc_fans = await self.rpc.fans()
            except APIError:
                return [Fan() for _ in range(self.expected_fans)]

        if rpc_fans is not None:
            try:
                response = BOSFansWrapper.model_validate(rpc_fans)
                fans = []
                for n in range(self.expected_fans):
                    if n < len(response.fans) and response.fans[n].rpm is not None:
                        fans.append(Fan(speed=response.fans[n].rpm))
                    else:
                        fans.append(Fan())
                return fans
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse fans: {e}")
                return [Fan() for _ in range(self.expected_fans)]
        return [Fan() for _ in range(self.expected_fans)]

    async def _get_errors(
        self, rpc_tunerstatus: dict[str, Any] | None = None
    ) -> list[MinerErrorData]:
        if rpc_tunerstatus is None:
            try:
                rpc_tunerstatus = await self.rpc.tunerstatus()
            except APIError:
                return []

        if rpc_tunerstatus is not None:
            errors = []
            try:
                response = BOSTunerStatusWrapper.model_validate(rpc_tunerstatus)
                if response.tunerstatus and response.tunerstatus[0].tuner_chain_status:
                    chain_status = response.tunerstatus[0].tuner_chain_status
                    if chain_status:
                        offset = (
                            6 if chain_status[0].hashchain_index in [6, 7, 8] else 0
                        )

                        for board in chain_status:
                            if board.hashchain_index is not None and board.status:
                                _id = board.hashchain_index - offset
                                if board.status not in [
                                    "Stable",
                                    "Testing performance profile",
                                    "Tuning individual chips",
                                ]:
                                    _error = board.status.split(" {")[0]
                                    _error = _error[0].lower() + _error[1:]
                                    errors.append(
                                        BraiinsOSError(
                                            error_message=f"Slot {_id} {_error}"
                                        )
                                    )
                return errors  # type: ignore
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse tunerstatus for errors: {e}")
        return []

    async def _get_fault_light(self) -> bool:
        if self.light:
            return self.light
        try:
            led_status_result = await self.ssh.get_led_status()
            if led_status_result is not None:
                data = led_status_result.strip()
                self.light = False
                if data == "50":
                    self.light = True
                return self.light
            else:
                return self.light or False
        except (TypeError, AttributeError):
            return self.light or False

    async def _get_expected_hashrate(
        self, rpc_devs: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if rpc_devs is None:
            try:
                rpc_devs = await self.rpc.devs()
            except APIError:
                return None

        if rpc_devs is not None:
            try:
                response = BOSDevsWrapper.model_validate(rpc_devs)
                hr_list = []

                for board in response.devs:
                    if board.nominal_mhs is not None:
                        expected_hashrate = float(board.nominal_mhs)
                        if expected_hashrate:
                            hr_list.append(expected_hashrate)

                if len(hr_list) == 0:
                    return self.algo.hashrate(
                        rate=float(0),
                        unit=self.algo.unit.default,  # type: ignore
                    )
                else:
                    return self.algo.hashrate(
                        rate=float(
                            (sum(hr_list) / len(hr_list))
                            * (self.expected_hashboards or 1)
                        ),
                        unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                    ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse devs for expected hashrate: {e}"
                )
        return None

    async def _is_mining(
        self, rpc_devdetails: dict[str, Any] | None = None
    ) -> bool | None:
        if rpc_devdetails is None:
            try:
                rpc_devdetails = await self.rpc.send_command(
                    "devdetails", ignore_errors=True, allow_warning=False
                )
            except APIError:
                return None

        if rpc_devdetails is not None:
            try:
                response = BOSStatusWrapper.model_validate(rpc_devdetails)
                if response.status:
                    return not response.status[0].msg == "Unavailable"
            except ValidationError:
                pass
        return None

    async def _get_uptime(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> int | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                return None

        if rpc_summary is not None:
            try:
                response = BOSSummaryWrapper.model_validate(rpc_summary)
                if response.summary and response.summary[0].elapsed is not None:
                    return int(response.summary[0].elapsed)
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse summary for uptime: {e}")
        return None

    async def _get_pools(
        self, rpc_pools: dict[str, Any] | None = None
    ) -> list[PoolMetrics]:
        if rpc_pools is None:
            try:
                rpc_pools = await self.rpc.pools()
            except APIError:
                return []

        pools_data = []
        if rpc_pools is not None:
            try:
                response = BOSPoolsWrapper.model_validate(rpc_pools)
                for pool_info in response.pools:
                    pool_url = (
                        PoolUrl.from_str(pool_info.url) if pool_info.url else None
                    )
                    pool_data = PoolMetrics(
                        accepted=pool_info.accepted,
                        rejected=pool_info.rejected,
                        get_failures=pool_info.get_failures,
                        remote_failures=pool_info.remote_failures,
                        active=pool_info.stratum_active,
                        alive=pool_info.status == "Alive",
                        url=pool_url,
                        user=pool_info.user,
                        index=pool_info.pool,
                    )
                    pools_data.append(pool_data)
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse pools: {e}")
        return pools_data

    async def upgrade_firmware(
        self,
        *,
        file: str | None = None,
        url: str | None = None,
        version: str | None = None,
        keep_settings: bool = True,
    ) -> bool:
        """
        Upgrade the firmware of the BOSMiner device.

        Args:
            file: The local file path of the firmware to be uploaded.
            url: URL of firmware to download (not used in this implementation).
            version: Specific version to upgrade to (not used in this implementation).
            keep_settings: Whether to keep current settings (not used in this implementation).

        Returns:
            True if upgrade was successful, False otherwise.
        """
        try:
            logging.info("Starting firmware upgrade process.")

            if not file:
                raise ValueError("File location must be provided for firmware upgrade.")

            # Read the firmware file contents
            async with aiofiles.open(file, "rb") as f:
                upgrade_contents = await f.read()

            # Encode the firmware contents in base64
            encoded_contents = base64.b64encode(upgrade_contents).decode("utf-8")

            # Upload the firmware file to the BOSMiner device
            logging.info(f"Uploading firmware file from {file} to the device.")
            await self.ssh.send_command(
                f"echo {encoded_contents} | base64 -d > /tmp/firmware.tar && sysupgrade /tmp/firmware.tar"
            )

            logging.info("Firmware upgrade process completed successfully.")
            return True
        except FileNotFoundError as e:
            logging.error(f"File not found during the firmware upgrade process: {e}")
            return False
        except ValueError as e:
            logging.error(
                f"Validation error occurred during the firmware upgrade process: {e}"
            )
            return False
        except OSError as e:
            logging.error(f"OS error occurred during the firmware upgrade process: {e}")
            return False
        except Exception as e:
            logging.error(
                f"An unexpected error occurred during the firmware upgrade process: {e}",
                exc_info=True,
            )
            return False


BOSER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [RPCAPICommand("rpc_version", "version")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [WebAPICommand("grpc_miner_details", "get_miner_details")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("grpc_hashboards", "get_hashboards")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("grpc_miner_stats", "get_miner_stats")],
        ),
        str(DataOptions.WATTAGE_LIMIT): DataFunction(
            "_get_wattage_limit",
            [
                WebAPICommand(
                    "grpc_active_performance_mode", "get_active_performance_mode"
                )
            ],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("grpc_cooling_state", "get_cooling_state")],
        ),
        str(DataOptions.ERRORS): DataFunction(
            "_get_errors",
            [RPCAPICommand("rpc_tunerstatus", "tunerstatus")],
        ),
        str(DataOptions.FAULT_LIGHT): DataFunction(
            "_get_fault_light",
            [WebAPICommand("grpc_locate_device_status", "get_locate_device_status")],
        ),
        str(DataOptions.IS_MINING): DataFunction(
            "_is_mining",
            [RPCAPICommand("rpc_devdetails", "devdetails")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [RPCAPICommand("rpc_summary", "summary")],
        ),
        str(DataOptions.POOLS): DataFunction(
            "_get_pools", [WebAPICommand("grpc_pool_groups", "get_pool_groups")]
        ),
    }
)


class BOSer(BraiinsOSFirmware):
    """Handler for new versions of BraiinsOS+ (post-gRPC)"""

    _rpc_cls = BOSMinerRPCAPI
    rpc: BOSMinerRPCAPI
    _web_cls = BOSerWebAPI
    web: BOSerWebAPI

    data_locations = BOSER_DATA_LOC

    supports_autotuning = True
    supports_shutdown = True

    async def fault_light_on(self) -> bool:
        resp = await self.web.set_locate_device_status(True)
        if resp.get("enabled", False):
            return True
        return False

    async def fault_light_off(self) -> bool:
        resp = await self.web.set_locate_device_status(False)
        if resp == {}:
            return True
        return False

    async def restart_backend(self) -> bool:
        return await self.restart_boser()

    async def restart_boser(self) -> bool:
        await self.web.restart()
        return True

    async def stop_mining(self) -> bool:
        try:
            await self.web.pause_mining()
        except APIError:
            return False
        return True

    async def resume_mining(self) -> bool:
        try:
            await self.web.resume_mining()
        except APIError:
            return False
        return True

    async def reboot(self) -> bool:
        ret = await self.web.reboot()
        if ret == {}:
            return True
        return False

    async def get_config(self) -> MinerConfig:
        grpc_conf = await self.web.get_miner_configuration()

        return MinerConfig.from_boser(grpc_conf)

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        boser_cfg = config.as_boser(user_suffix=user_suffix)
        for key in boser_cfg:
            await self.web.send_command(key, message=boser_cfg[key])

    async def set_power_limit(self, wattage: int) -> bool:
        try:
            result = await self.web.set_power_target(
                wattage,
                save_action=SaveAction(SaveAction.SAVE_AND_FORCE_APPLY),
            )
        except APIError:
            return False

        try:
            if result["powerTarget"]["watt"] == wattage:
                return True
        except KeyError:
            pass
        return False

    ##################################################
    ### DATA GATHERING FUNCTIONS (get_{some_data}) ###
    ##################################################

    async def _get_mac(
        self, grpc_miner_details: dict[str, Any] | None = None
    ) -> str | None:
        if grpc_miner_details is None:
            try:
                grpc_miner_details = await self.web.get_miner_details()
            except APIError:
                return None

        if grpc_miner_details is not None:
            try:
                response = BOSerMinerDetails.model_validate(grpc_miner_details)
                if response.mac_address:
                    return response.mac_address.upper()
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse miner details for MAC: {e}")
        return None

    async def _get_api_ver(
        self, rpc_version: dict[str, Any] | None = None
    ) -> str | None:
        if rpc_version is None:
            try:
                rpc_version = await self.rpc.version()
            except APIError:
                return None

        if rpc_version is not None:
            try:
                rpc_ver = rpc_version["VERSION"][0]["API"]
            except LookupError:
                rpc_ver = None
            self.api_ver = rpc_ver
            self.rpc.rpc_ver = self.api_ver  # type: ignore

        return self.api_ver

    async def _get_fw_ver(
        self, grpc_miner_details: dict[str, Any] | None = None
    ) -> str | None:
        if grpc_miner_details is None:
            try:
                grpc_miner_details = await self.web.get_miner_details()
            except APIError:
                return None

        if grpc_miner_details is not None:
            try:
                response = BOSerMinerDetails.model_validate(grpc_miner_details)
                if response.bos_version and response.bos_version.current:
                    fw_ver = response.bos_version.current
                    ver = fw_ver.split("-")[5]
                    if "." in ver:
                        self.fw_ver = ver
            except (ValidationError, IndexError) as e:
                logger.warning(f"{self} - Failed to parse firmware version: {e}")

        return self.fw_ver

    async def _get_hostname(
        self, grpc_miner_details: dict[str, Any] | None = None
    ) -> str | None:
        if grpc_miner_details is None:
            try:
                grpc_miner_details = await self.web.get_miner_details()
            except APIError:
                return None

        if grpc_miner_details is not None:
            try:
                response = BOSerMinerDetails.model_validate(grpc_miner_details)
                return response.hostname
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse hostname: {e}")
        return None

    async def _get_hashrate(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                return None

        if rpc_summary is not None:
            try:
                response = BOSSummaryWrapper.model_validate(rpc_summary)
                if response.summary and response.summary[0].mhs_1m is not None:
                    return self.algo.hashrate(
                        rate=float(response.summary[0].mhs_1m),
                        unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                    ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse summary for hashrate: {e}")
        return None

    async def _get_expected_hashrate(
        self, grpc_miner_details: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if grpc_miner_details is None:
            try:
                grpc_miner_details = await self.web.get_miner_details()
            except APIError:
                return None

        if grpc_miner_details is not None:
            try:
                response = BOSerMinerDetails.model_validate(grpc_miner_details)
                if (
                    response.sticker_hashrate
                    and response.sticker_hashrate.gigahashPerSecond is not None
                ):
                    return self.algo.hashrate(
                        rate=float(response.sticker_hashrate.gigahashPerSecond),
                        unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                    ).into(self.algo.unit.default)  # type: ignore[attr-defined]
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse expected hashrate: {e}")
        return None

    async def _get_hashboards(
        self, grpc_hashboards: dict[str, Any] | None = None
    ) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        hashboards = [
            HashBoard(slot=i, expected_chips=self.expected_chips)
            for i in range(self.expected_hashboards)
        ]

        if grpc_hashboards is None:
            try:
                grpc_hashboards = await self.web.get_hashboards()
            except APIError:
                return hashboards

        if grpc_hashboards is not None:
            try:
                response = BOSerHashBoards.model_validate(grpc_hashboards)
                grpc_boards = sorted(
                    response.hashboards, key=lambda x: int(x.id) if x.id else 0
                )
                for idx, board in enumerate(grpc_boards):
                    if idx < len(hashboards):
                        if board.chips_count is not None:
                            hashboards[idx].chips = board.chips_count
                        if board.board_temp and board.board_temp.degree_c is not None:
                            hashboards[idx].temp = int(board.board_temp.degree_c)
                        if (
                            board.highest_chip_temp
                            and board.highest_chip_temp.temperature
                            and board.highest_chip_temp.temperature.degree_c is not None
                        ):
                            hashboards[idx].chip_temp = int(
                                board.highest_chip_temp.temperature.degree_c
                            )
                        if board.stats and board.stats.real_hashrate:
                            last_5s = board.stats.real_hashrate.get("last5S")
                            if (
                                last_5s
                                and isinstance(last_5s, dict)
                                and last_5s.get("gigahashPerSecond") is not None
                            ):
                                hashboards[idx].hashrate = self.algo.hashrate(
                                    rate=float(last_5s["gigahashPerSecond"]),
                                    unit=self.algo.unit.GH,
                                ).into(self.algo.unit.default)
                        hashboards[idx].missing = False
            except (ValidationError, ValueError) as e:
                logger.warning(f"{self} - Failed to parse hashboards: {e}")

        return hashboards

    async def _get_wattage(
        self, grpc_miner_stats: dict[str, Any] | None = None
    ) -> int | None:
        if grpc_miner_stats is None:
            try:
                grpc_miner_stats = await self.web.get_miner_stats()
            except APIError:
                return None

        if grpc_miner_stats is not None:
            try:
                response = BOSerMinerStats.model_validate(grpc_miner_stats)
                if (
                    response.power_stats
                    and response.power_stats.approximated_consumption
                    and response.power_stats.approximated_consumption.watt is not None
                ):
                    return int(response.power_stats.approximated_consumption.watt)
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse power stats: {e}")
        return None

    async def _get_wattage_limit(
        self, grpc_active_performance_mode: dict[str, Any] | None = None
    ) -> int | None:
        if grpc_active_performance_mode is None:
            try:
                grpc_active_performance_mode = (
                    await self.web.get_active_performance_mode()
                )
            except APIError:
                return None

        if grpc_active_performance_mode is not None:
            try:
                response = BOSerActivePerformanceMode.model_validate(
                    grpc_active_performance_mode
                )
                if response.tuner_mode and response.tuner_mode.power_target:
                    power_target = response.tuner_mode.power_target.get("powerTarget")
                    if isinstance(power_target, dict) and "watt" in power_target:
                        return int(power_target["watt"])
            except (ValidationError, ValueError) as e:
                logger.warning(f"{self} - Failed to parse wattage limit: {e}")
        return None

    async def _get_fans(
        self, grpc_cooling_state: dict[str, Any] | None = None
    ) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if grpc_cooling_state is None:
            try:
                grpc_cooling_state = await self.web.get_cooling_state()
            except APIError:
                return [Fan() for _ in range(self.expected_fans)]

        if grpc_cooling_state is not None:
            try:
                response = BOSerCoolingState.model_validate(grpc_cooling_state)
                fans = []
                for n in range(self.expected_fans):
                    if n < len(response.fans) and response.fans[n].rpm is not None:
                        fans.append(Fan(speed=response.fans[n].rpm))
                    else:
                        fans.append(Fan())
                return fans
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse cooling state: {e}")
        return [Fan() for _ in range(self.expected_fans)]

    async def _get_errors(
        self, rpc_tunerstatus: dict[str, Any] | None = None
    ) -> list[MinerErrorData]:
        if rpc_tunerstatus is None:
            try:
                rpc_tunerstatus = await self.rpc.tunerstatus()
            except APIError:
                return []

        if rpc_tunerstatus is not None:
            errors = []
            try:
                response = BOSTunerStatusWrapper.model_validate(rpc_tunerstatus)
                if response.tunerstatus and response.tunerstatus[0].tuner_chain_status:
                    chain_status = response.tunerstatus[0].tuner_chain_status
                    if chain_status:
                        offset = (
                            6 if chain_status[0].hashchain_index in [6, 7, 8] else 0
                        )

                        for board in chain_status:
                            if board.hashchain_index is not None and board.status:
                                _id = board.hashchain_index - offset
                                if board.status not in [
                                    "Stable",
                                    "Testing performance profile",
                                    "Tuning individual chips",
                                ]:
                                    _error = board.status.split(" {")[0]
                                    _error = _error[0].lower() + _error[1:]
                                    errors.append(
                                        BraiinsOSError(
                                            error_message=f"Slot {_id} {_error}"
                                        )
                                    )
                return errors  # type: ignore
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse tunerstatus for errors: {e}")
        return []

    async def _get_fault_light(
        self, grpc_locate_device_status: dict[str, Any] | None = None
    ) -> bool:
        if self.light is not None:
            return self.light

        if grpc_locate_device_status is None:
            try:
                grpc_locate_device_status = await self.web.get_locate_device_status()
            except APIError:
                return False

        if grpc_locate_device_status is not None:
            if grpc_locate_device_status == {}:
                return False
            try:
                response = BOSerLocateDeviceStatus.model_validate(
                    grpc_locate_device_status
                )
                if isinstance(response.enabled, bool):
                    return response.enabled
            except ValidationError:
                pass
        return False

    async def _is_mining(
        self, rpc_devdetails: dict[str, Any] | None = None
    ) -> bool | None:
        if rpc_devdetails is None:
            try:
                rpc_devdetails = await self.rpc.send_command(
                    "devdetails", ignore_errors=True, allow_warning=False
                )
            except APIError:
                return None

        if rpc_devdetails is not None:
            try:
                response = BOSStatusWrapper.model_validate(rpc_devdetails)
                if response.status:
                    return not response.status[0].msg == "Unavailable"
            except ValidationError:
                # If validation fails, might still be mining
                pass
        return None

    async def _get_uptime(
        self, rpc_summary: dict[str, Any] | None = None
    ) -> int | None:
        if rpc_summary is None:
            try:
                rpc_summary = await self.rpc.summary()
            except APIError:
                return None

        if rpc_summary is not None:
            try:
                response = BOSSummaryWrapper.model_validate(rpc_summary)
                if response.summary and response.summary[0].elapsed is not None:
                    return int(response.summary[0].elapsed)
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse summary for uptime: {e}")
        return None

    async def _get_pools(
        self, grpc_pool_groups: dict[str, Any] | None = None
    ) -> list[PoolMetrics]:
        if grpc_pool_groups is None:
            try:
                grpc_pool_groups = await self.web.get_pool_groups()
            except APIError:
                return []

        pools_data = []
        if grpc_pool_groups is not None:
            try:
                response = BOSerPoolGroups.model_validate(grpc_pool_groups)
                for group in response.pool_groups:
                    for idx, pool_info in enumerate(group.pools):
                        pool_data = PoolMetrics(
                            url=PoolUrl.from_str(pool_info.url)
                            if pool_info.url
                            else None,
                            user=pool_info.user,
                            index=idx,
                            accepted=pool_info.stats.accepted_shares
                            if pool_info.stats
                            else 0,
                            rejected=pool_info.stats.rejected_shares
                            if pool_info.stats
                            else 0,
                            get_failures=0,
                            remote_failures=0,
                            active=pool_info.active,
                            alive=pool_info.alive,
                        )
                        pools_data.append(pool_data)
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse pool groups: {e}")

        return pools_data
