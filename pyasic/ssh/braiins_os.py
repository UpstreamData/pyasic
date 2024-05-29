import tempfile
from pyasic import settings
from pyasic.ssh.base import BaseSSH
import logging
import httpx
from pathlib import Path
import hashlib
from pyasic.miners.base import FirmwareManager

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class BOSMinerSSH(BaseSSH):
    def __init__(self, ip: str):
        """
        Initialize a BOSMinerSSH instance.

        Args:
            ip (str): The IP address of the BOSMiner device.
        """
        super().__init__(ip)
        self.pwd = settings.get("default_bosminer_ssh_password", "root")
        self.firmware_manager = FirmwareManager()

    def get_firmware_version(self, firmware_file):
        """
        Extract the firmware version from the firmware file.

        Args:
            firmware_file (file): The firmware file to extract the version from.

        Returns:
            str: The firmware version.
        """
        import re

        # Extract the version from the filename using a regular expression
        filename = firmware_file.name
        match = re.search(r"firmware_v(\d+\.\d+\.\d+)\.tar\.gz", filename)
        if match:
            return match.group(1)
        else:
            raise ValueError("Firmware version not found in the filename.")

    async def get_board_info(self):
        """
        Retrieve information about the BOSMiner board.

        Returns:
            str: Information about the BOSMiner board.
        """
        return await self.send_command("bosminer model -d")

    async def fault_light_on(self):
        """
        Turn on the fault light of the BOSMiner device.

        Returns:
            str: Confirmation message after turning on the fault light.
        """
        return await self.send_command("miner fault_light on")

    async def fault_light_off(self):
        """
        Turn off the fault light of the BOSMiner device.

        Returns:
            str: Confirmation message after turning off the fault light.
        """
        return await self.send_command("miner fault_light off")

    async def restart_bosminer(self):
        """
        Restart the BOSMiner service on the device.

        Returns:
            str: Confirmation message after restarting the BOSMiner service.
        """
        return await self.send_command("/etc/init.d/bosminer restart")

    async def reboot(self):
        """
        Reboot the BOSMiner device.

        Returns:
            str: Confirmation message after initiating the reboot process.
        """
        return await self.send_command("/sbin/reboot")

    async def get_config_file(self):
        """
        Retrieve the configuration file of BOSMiner.

        Returns:
            str: Content of the BOSMiner configuration file.
        """
        return await self.send_command("cat /etc/bosminer.toml")

    async def get_network_config(self):
        """
        Retrieve the network configuration of the BOSMiner device.

        Returns:
            str: Content of the network configuration file.
        """
        return await self.send_command("cat /etc/config/network")

    async def get_hostname(self):
        """
        Retrieve the hostname of the BOSMiner device.

        Returns:
            str: Hostname of the BOSMiner device.
        """
        return await self.send_command("cat /proc/sys/kernel/hostname")

    async def get_led_status(self):
        """
        Retrieve the status of the LED on the BOSMiner device.

        Returns:
            str: Status of the LED.
        """
        return await self.send_command("cat /sys/class/leds/'Red LED'/delay_off")

    async def upgrade_firmware(self, file_location: str = None, custom_url: str = None, override_validation: bool = False):
        """
        Upgrade the firmware of the BOSMiner device.

        Args:
            file_location (str): The local file path of the firmware to be uploaded. If not provided, the firmware will be downloaded from the internal server.
            custom_url (str): Custom URL to download the firmware from.
            override_validation (bool): Whether to override SHA256 validation.

        Returns:
            str: Confirmation message after upgrading the firmware.
        """
        try:
            logger.info("Starting firmware upgrade process.")

            if file_location is None:
                # Check for cached firmware file
                with tempfile.NamedTemporaryFile(delete=False) as temp_firmware_file:
                    cached_file_location = Path(temp_firmware_file.name)
                if cached_file_location.exists():
                    logger.info("Cached firmware file found. Checking version.")
                    # Compare cached firmware version with the latest version on the server
                    latest_firmware_info = await self.firmware_manager.get_latest_firmware_info()
                    latest_version = latest_firmware_info.get("version")
                    latest_hash = latest_firmware_info.get("sha256")
                    cached_version = self.firmware_manager.get_firmware_version("braiins_os", cached_file_location)
                    if cached_version == latest_version:
                        logger.info("Cached firmware version matches the latest version. Using cached file.")
                        file_location = str(cached_file_location)
                    else:
                        logger.info("Cached firmware version does not match the latest version. Downloading new version.")
                        firmware_url = custom_url or latest_firmware_info.get("url")
                        if not firmware_url:
                            raise ValueError("Firmware URL not found in the server response.")
                        await self.firmware_manager.download_firmware(firmware_url, cached_file_location)
                        if not override_validation:
                            downloaded_hash = self.firmware_manager.calculate_sha256(cached_file_location)
                            if downloaded_hash != latest_hash:
                                raise ValueError("SHA256 hash validation failed for the downloaded firmware file.")
                        file_location = str(cached_file_location)
                else:
                    logger.info("No cached firmware file found. Downloading new version.")
                    latest_firmware_info = await self.firmware_manager.get_latest_firmware_info()
                    firmware_url = custom_url or latest_firmware_info.get("url")
                    latest_hash = latest_firmware_info.get("sha256")
                    if not firmware_url:
                        raise ValueError("Firmware URL not found in the server response.")
                    await self.firmware_manager.download_firmware(firmware_url, cached_file_location)
                    if not override_validation:
                        downloaded_hash = self.firmware_manager.calculate_sha256(cached_file_location)
                        if downloaded_hash != latest_hash:
                            raise ValueError("SHA256 hash validation failed for the downloaded firmware file.")
                    file_location = str(cached_file_location)

            # Upload the firmware file to the BOSMiner device
            logger.info(f"Uploading firmware file from {file_location} to the device.")
            await self.send_command(f"scp {file_location} root@{self.ip}:/tmp/firmware.tar.gz")

            # Extract the firmware file
            logger.info("Extracting the firmware file on the device.")
            await self.send_command("tar -xzf /tmp/firmware.tar.gz -C /tmp")

            # Run the firmware upgrade script
            logger.info("Running the firmware upgrade script on the device.")
            result = await self.send_command("sh /tmp/upgrade_firmware.sh")

            logger.info("Firmware upgrade process completed successfully.")
            return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred during the firmware upgrade process: {e}")
            raise
        except FileNotFoundError as e:
            logger.error(f"File not found during the firmware upgrade process: {e}")
            raise
        except ValueError as e:
            logger.error(f"Validation error occurred during the firmware upgrade process: {e}")
            raise
        except OSError as e:
            logger.error(f"OS error occurred during the firmware upgrade process: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during the firmware upgrade process: {e}", exc_info=True)
            raise