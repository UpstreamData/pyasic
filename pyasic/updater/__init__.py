from pathlib import Path
from pyasic.updater.bos import FirmwareManager

class FirmwareUpdater:
    def __init__(self, firmware, raw_model, ssh_client):
        """
        Initialize a FirmwareUpdater instance.

        Args:
            firmware: The firmware type of the miner.
            raw_model: The raw model of the miner.
            ssh_client: The SSH client to use for sending commands to the device.
        """
        self.firmware = firmware
        self.raw_model = raw_model
        self.ssh_client = ssh_client
        self.manager = self._get_manager()

    def _get_manager(self):
        """
        Get the appropriate firmware manager based on the firmware type and raw model.

        Returns:
            The firmware manager instance.
        """
        if self.firmware == "braiins_os":
            return FirmwareManager(self.ssh_client)
        # Add more conditions here for different firmware types and raw models
        else:
            raise ValueError(f"Unsupported firmware type: {self.firmware}")

    async def upgrade_firmware(self, file: Path):
        """
        Upgrade the firmware of the miner.

        Args:
            file (Path): The local file path of the firmware to be uploaded.

        Returns:
            str: Confirmation message after upgrading the firmware.
        """
        return await self.manager.upgrade_firmware(file)
