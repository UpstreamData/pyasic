from typing import Any

from pydantic import BaseModel, ValidationError

from pyasic.config import MinerConfig
from pyasic.data.boards import HashBoard
from pyasic.data.fans import Fan
from pyasic.device.algorithm.hashrate.base import AlgoHashRateType
from pyasic.device.firmware import MinerFirmware
from pyasic.errors import APIError
from pyasic.logger import logger
from pyasic.miners.base import BaseMiner
from pyasic.miners.data import DataFunction, DataLocations, DataOptions, WebAPICommand
from pyasic.web.espminer import ESPMinerWebAPI


class ESPMinerSystemInfo(BaseModel):
    power: float | int | None = None
    hashRate: float = 0
    smallCoreCount: int | None = None
    asicCount: int | None = None
    frequency: float | None = None
    uptimeSeconds: int = 0
    temp: float | None = None
    vrTemp: float | None = None
    voltage: float | None = None
    fanrpm: int | None = None
    hostname: str = ""
    version: str = ""
    macAddr: str = ""

    class Config:
        extra = "allow"


class ESPMinerAsicInfo(BaseModel):
    asicCount: int | None = None

    class Config:
        extra = "allow"


ESPMINER_DATA_LOC = DataLocations(
    **{
        str(DataOptions.HASHRATE): DataFunction(
            "_get_hashrate",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.EXPECTED_HASHRATE): DataFunction(
            "_get_expected_hashrate",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.WATTAGE): DataFunction(
            "_get_wattage",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.UPTIME): DataFunction(
            "_get_uptime",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.HASHBOARDS): DataFunction(
            "_get_hashboards",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.HOSTNAME): DataFunction(
            "_get_hostname",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.FANS): DataFunction(
            "_get_fans",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.FW_VERSION): DataFunction(
            "_get_fw_ver",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.API_VERSION): DataFunction(
            "_get_api_ver",
            [WebAPICommand("web_system_info", "system/info")],
        ),
        str(DataOptions.MAC): DataFunction(
            "_get_mac",
            [WebAPICommand("web_system_info", "system/info")],
        ),
    }
)


class ESPMiner(BaseMiner):
    """Handler for ESPMiner"""

    web: ESPMinerWebAPI
    _web_cls = ESPMinerWebAPI

    firmware = MinerFirmware.STOCK

    data_locations = ESPMINER_DATA_LOC

    async def reboot(self) -> bool:
        await self.web.restart()
        return True

    async def get_config(self) -> MinerConfig:
        web_system_info = await self.web.system_info()
        return MinerConfig.from_espminer(web_system_info)

    async def send_config(
        self, config: MinerConfig, user_suffix: str | None = None
    ) -> None:
        await self.web.update_settings(**config.as_espminer())

    async def _get_wattage(
        self, web_system_info: dict[str, Any] | None = None
    ) -> int | None:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                if system_info.power is not None:
                    return round(system_info.power)
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse system info for wattage: {e}")
        return None

    async def _get_hashrate(
        self, web_system_info: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                return self.algo.hashrate(
                    rate=system_info.hashRate,
                    unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                ).into(
                    self.algo.unit.default  # type: ignore[attr-defined]
                )
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse system info for hashrate: {e}"
                )
        return None

    async def _get_expected_hashrate(
        self, web_system_info: dict[str, Any] | None = None
    ) -> AlgoHashRateType | None:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                small_core_count = system_info.smallCoreCount
                asic_count = system_info.asicCount
                frequency = system_info.frequency

                if asic_count is None:
                    try:
                        asic_info_data = await self.web.asic_info()
                        asic_info = ESPMinerAsicInfo.model_validate(asic_info_data)
                        asic_count = asic_info.asicCount
                    except (APIError, ValidationError):
                        pass

                if (
                    small_core_count is not None
                    and asic_count is not None
                    and frequency is not None
                ):
                    expected_hashrate = small_core_count * asic_count * frequency
                    return self.algo.hashrate(
                        rate=float(expected_hashrate),
                        unit=self.algo.unit.MH,  # type: ignore[attr-defined]
                    ).into(
                        self.algo.unit.default  # type: ignore[attr-defined]
                    )
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse system info for expected hashrate: {e}"
                )
        return None

    async def _get_uptime(
        self, web_system_info: dict[str, Any] | None = None
    ) -> int | None:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                return system_info.uptimeSeconds
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse system info for uptime: {e}")
        return None

    async def _get_hashboards(
        self, web_system_info: dict[str, Any] | None = None
    ) -> list[HashBoard]:
        if self.expected_hashboards is None:
            return []

        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                return [
                    HashBoard(
                        hashrate=self.algo.hashrate(
                            rate=system_info.hashRate,
                            unit=self.algo.unit.GH,  # type: ignore[attr-defined]
                        ).into(
                            self.algo.unit.default  # type: ignore[attr-defined]
                        ),
                        chip_temp=system_info.temp,
                        temp=system_info.vrTemp,
                        chips=system_info.asicCount or 1,
                        expected_chips=self.expected_chips,
                        missing=False,
                        active=True,
                        voltage=system_info.voltage,
                    )
                ]
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse system info for hashboards: {e}"
                )
        return []

    async def _get_fans(
        self, web_system_info: dict[str, Any] | None = None
    ) -> list[Fan]:
        if self.expected_fans is None:
            return []

        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                if system_info.fanrpm is not None:
                    return [Fan(speed=system_info.fanrpm)]
            except ValidationError as e:
                logger.warning(f"{self} - Failed to parse system info for fans: {e}")
        return []

    async def _get_hostname(
        self, web_system_info: dict[str, Any] | None = None
    ) -> str | None:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                return system_info.hostname if system_info.hostname else None
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse system info for hostname: {e}"
                )
        return None

    async def _get_api_ver(
        self, web_system_info: dict[str, Any] | None = None
    ) -> str | None:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                return system_info.version if system_info.version else None
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse system info for API version: {e}"
                )
        return None

    async def _get_fw_ver(
        self, web_system_info: dict[str, Any] | None = None
    ) -> str | None:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                return system_info.version if system_info.version else None
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse system info for firmware version: {e}"
                )
        return None

    async def _get_mac(
        self, web_system_info: dict[str, Any] | None = None
    ) -> str | None:
        if web_system_info is None:
            try:
                web_system_info = await self.web.system_info()
            except APIError:
                pass

        if web_system_info is not None:
            try:
                system_info = ESPMinerSystemInfo.model_validate(web_system_info)
                return system_info.macAddr.upper() if system_info.macAddr else None
            except ValidationError as e:
                logger.warning(
                    f"{self} - Failed to parse system info for MAC address: {e}"
                )
        return None
