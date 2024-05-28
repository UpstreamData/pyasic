from pyasic import settings
from pyasic.ssh.base import BaseSSH
import logging
import requests
import os

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

    async def upgrade_firmware(self, file_location: str = None):
        """
        Upgrade the firmware of the BOSMiner device.

        Args:
            file_location (str): The local file path of the firmware to be uploaded. If not provided, the firmware will be downloaded from the internal server.

        Returns:
            str: Confirmation message after upgrading the firmware.
        """
        try:
            logger.info("Starting firmware upgrade process.")

            if file_location is None:
                # Check for cached firmware file
                cached_file_location = "/tmp/cached_firmware.tar.gz"
                if os.path.exists(cached_file_location):
                    logger.info("Cached firmware file found. Checking version.")
                    # Compare cached firmware version with the latest version on the server
                    response = requests.get("http://firmware.pyasic.org/latest")
                    response.raise_for_status()
                    latest_version = response.json().get("version")
                    cached_version = self._get_fw_ver()
                    
                    if cached_version == latest_version:
                        logger.info("Cached firmware version matches the latest version. Using cached file.")
                        file_location = cached_file_location
                    else:
                        logger.info("Cached firmware version does not match the latest version. Downloading new version.")
                        firmware_url = response.json().get("url")
                        if not firmware_url:
                            raise ValueError("Firmware URL not found in the server response.")
                        firmware_response = requests.get(firmware_url)
                        firmware_response.raise_for_status()
                        with open(cached_file_location, "wb") as firmware_file:
                            firmware_file.write(firmware_response.content)
                        file_location = cached_file_location
                else:
                    logger.info("No cached firmware file found. Downloading new version.")
                    response = requests.get("http://firmware.pyasic.org/latest")
                    response.raise_for_status()
                    firmware_url = response.json().get("url")
                    if not firmware_url:
                        raise ValueError("Firmware URL not found in the server response.")
                    firmware_response = requests.get(firmware_url)
                    firmware_response.raise_for_status()
                    with open(cached_file_location, "wb") as firmware_file:
                        firmware_file.write(firmware_response.content)
                    file_location = cached_file_location

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
        except Exception as e:
            logger.error(f"An error occurred during the firmware upgrade process: {e}")
            raise