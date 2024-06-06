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
from pyasic.miners.backends.btminer import BTMiner
import asyncio
import json
import struct
import logging
from pathlib import Path
import aiofiles


class M6X(BTMiner):
    supports_autotuning = True


class M5X(BTMiner):
    supports_autotuning = True


class M3X(BTMiner):
    supports_autotuning = True


class M2X(BTMiner):
    pass


class Whatsminer(BTMiner):
    async def upgrade_firmware(self, file: Path, token: str):
        """
        Upgrade the firmware of the Whatsminer device.

        Args:
            file (Path): The local file path of the firmware to be uploaded.
            token (str): The authentication token for the firmware upgrade.

        Returns:
            str: Confirmation message after upgrading the firmware.
        """
        try:
            logging.info("Starting firmware upgrade process for Whatsminer.")

            if not file:
                raise ValueError("File location must be provided for firmware upgrade.")

            # Read the firmware file contents
            async with aiofiles.open(file, "rb") as f:
                upgrade_contents = await f.read()

            # Establish a TCP connection to the miner
            reader, writer = await asyncio.open_connection(self.ip, self.port)

            # Send the update_firmware command
            command = json.dumps({"token": token, "cmd": "update_firmware"})
            writer.write(command.encode())
            await writer.drain()

            # Wait for the miner to respond with "ready"
            response = await reader.read(1024)
            response_json = json.loads(response.decode())
            if response_json.get("Msg") != "ready":
                raise Exception("Miner is not ready for firmware upgrade.")

            # Send the firmware file size and data
            file_size = struct.pack("<I", len(upgrade_contents))
            writer.write(file_size)
            writer.write(upgrade_contents)
            await writer.drain()

            # Close the connection
            writer.close()
            await writer.wait_closed()

            logging.info("Firmware upgrade process completed successfully for Whatsminer.")
            return "Firmware upgrade completed successfully."
        except FileNotFoundError as e:
            logging.error(f"File not found during the firmware upgrade process: {e}")
            raise
        except ValueError as e:
            logging.error(f"Validation error occurred during the firmware upgrade process: {e}")
            raise
        except OSError as e:
            logging.error(f"OS error occurred during the firmware upgrade process: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred during the firmware upgrade process: {e}", exc_info=True)
            raise
