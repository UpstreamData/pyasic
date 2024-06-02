import httpx
from pathlib import Path
import re
import hashlib
import aiofiles
import logging

class FirmwareManager:
    def __init__(self, ssh_client):
        """
        Initialize a FirmwareManager instance.

        Args:
            ssh_client: The SSH client to use for sending commands to the device.
        """
        self.remote_server_url = "http://feeds.braiins-os.com"
        self.version_extractors = {}
        self.ssh = ssh_client

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Register version extractor for braiins_os
        self.register_version_extractor("braiins_os", self.extract_braiins_os_version)

    def extract_braiins_os_version(self, firmware_file: Path) -> str:
        """
        Extract the firmware version from the filename for braiins_os miners.

        Args:
            firmware_file (Path): The firmware file to extract the version from.

        Returns:
            str: The extracted firmware version.

        Raises:
            ValueError: If the version is not found in the filename.
        """
        match = re.search(r"(am1_s9|am2_x17|am3_bbb)/firmware_v(\d+\.\d+\.\d+)\.tar", firmware_file.name)
        if match:
            return match.group(2)
        raise ValueError("Firmware version not found in the filename.")

    async def get_latest_firmware_info(self) -> dict:
        """
        Fetch the latest firmware information from the remote server.

        Returns:
            dict: The latest firmware information, including version and SHA256 hash.

        Raises:
            httpx.HTTPStatusError: If the HTTP request fails.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.remote_server_url}/latest")
        response.raise_for_status()
        return response.json()

    async def download_firmware(self, url: str, file_path: Path):
        """
        Download the firmware file from the specified URL and save it to the given file path.

        Args:
            url (str): The URL to download the firmware from.
            file_path (Path): The file path to save the downloaded firmware.

        Raises:
            httpx.HTTPStatusError: If the HTTP request fails.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        response.raise_for_status()
        with file_path.open("wb") as firmware_file:
            firmware_file.write(response.content)

    def calculate_sha256(self, file_path: Path) -> str:
        """
        Calculate the SHA256 hash of the specified file.

        Args:
            file_path (Path): The file path of the file to calculate the hash for.

        Returns:
            str: The SHA256 hash of the file.
        """
        sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def register_version_extractor(self, miner_type: str, extractor_func):
        """
        Register a custom firmware version extraction function for a specific miner type.

        Args:
            miner_type (str): The type of miner.
            extractor_func (function): The function to extract the firmware version from the firmware file.
        """
        self.version_extractors[miner_type] = extractor_func

    def get_firmware_version(self, miner_type: str, firmware_file: Path) -> str:
        """
        Extract the firmware version from the firmware file using the registered extractor function for the miner type.

        Args:
            miner_type (str): The type of miner.
            firmware_file (Path): The firmware file to extract the version from.

        Returns:
            str: The firmware version.

        Raises:
            ValueError: If no extractor function is registered for the miner type or if the version is not found.
        """
        if miner_type not in self.version_extractors:
            raise ValueError(f"No version extractor registered for miner type: {miner_type}")

        extractor_func = self.version_extractors[miner_type]
        return extractor_func(firmware_file)

    async def upgrade_firmware(self, file: Path):
        """
        Upgrade the firmware of the BOSMiner device.

        Args:
            file (Path): The local file path of the firmware to be uploaded.

        Returns:
            str: Confirmation message after upgrading the firmware.
        """
        try:
            self.logger.info("Starting firmware upgrade process.")

            if not file:
                raise ValueError("File location must be provided for firmware upgrade.")

            # Read the firmware file contents
            async with aiofiles.open(file, "rb") as f:
                upgrade_contents = await f.read()

            # Encode the firmware contents in base64
            import base64
            encoded_contents = base64.b64encode(upgrade_contents).decode('utf-8')

            # Upload the firmware file to the BOSMiner device
            self.logger.info(f"Uploading firmware file from {file} to the device.")
            await self.ssh.send_command(f"echo {encoded_contents} | base64 -d > /tmp/firmware.tar && sysupgrade /tmp/firmware.tar")

            self.logger.info("Firmware upgrade process completed successfully.")
            return "Firmware upgrade completed successfully."
        except FileNotFoundError as e:
            self.logger.error(f"File not found during the firmware upgrade process: {e}")
            raise
        except ValueError as e:
            self.logger.error(f"Validation error occurred during the firmware upgrade process: {e}")
            raise
        except OSError as e:
            self.logger.error(f"OS error occurred during the firmware upgrade process: {e}")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during the firmware upgrade process: {e}", exc_info=True)
            raise
