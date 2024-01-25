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

from pyasic.rpc.base import BaseMinerRPCAPI


class GCMinerRPCAPI(BaseMinerRPCAPI):
    """An abstraction of the GCMiner API.

    Each method corresponds to an API command in GCMiner.

    No documentation for this API is currently publicly available.

    This class abstracts use of the GCMiner API, as well as the
    methods for sending commands to it.  The `self.send_command()`
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.
    """

    async def asc(self, n: int) -> dict:
        """Get data for ASC device n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The device to get data for.

        Returns:
            The data for ASC device n.
        </details>
        """
        return await self.send_command("asc", parameters=n)

    async def asccount(self) -> dict:
        """Get data on the number of ASC devices and their info.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on all ASC devices.
        </details>
        """
        return await self.send_command("asccount")

    async def check(self, command: str) -> dict:
        """Check if the command `command` exists in LUXMiner.
        <details>
            <summary>Expand</summary>

        Parameters:
            command: The command to check.

        Returns:
            ## Information about a command:
                * Exists (Y/N) <- the command exists in this version
                * Access (Y/N) <- you have access to use the command
        </details>
        """
        return await self.send_command("check", parameters=command)

    async def coin(self) -> dict:
        """Get information on the current coin.
        <details>
            <summary>Expand</summary>

        Returns:
            ## Information about the current coin being mined:
                * Hash Method <- the hashing algorithm
                * Current Block Time <- blocktime as a float, 0 means none
                * Current Block Hash <- the hash of the current block, blank means none
                * LP <- whether LP is in use on at least 1 pool
                * Network Difficulty: the current network difficulty
        </details>
        """
        return await self.send_command("coin")

    async def config(self) -> dict:
        """Get some basic configuration info.
        <details>
            <summary>Expand</summary>

        Returns:
            Miner configuration information.
        </details>
        """
        return await self.send_command("config")

    async def devdetails(self) -> dict:
        """Get data on all devices with their static details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on all devices with their static details.
        </details>
        """
        return await self.send_command("devdetails")

    async def devs(self) -> dict:
        """Get data on each PGA/ASC with their details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on each PGA/ASC with their details.
        </details>
        """
        return await self.send_command("devs")

    async def edevs(self) -> dict:
        """Alias for devs"""
        return await self.send_command("edevs")

    async def pools(self) -> dict:
        """Get pool information.

        <details>
            <summary>Expand</summary>

        Returns:
            Miner pool information.
        </details>
        """
        return await self.send_command("pools")

    async def stats(self) -> dict:
        """Get stats of each device/pool with more than 1 getwork.

        <details>
            <summary>Expand</summary>

        Returns:
            Stats of each device/pool with more than 1 getwork.
        </details>
        """
        return await self.send_command("stats")

    async def estats(self) -> dict:
        """Alias for stats"""
        return await self.send_command("estats")

    async def summary(self) -> dict:
        """Get the status summary of the miner.

        <details>
            <summary>Expand</summary>

        Returns:
            The status summary of the miner.
        </details>
        """
        return await self.send_command("summary")

    async def version(self) -> dict:
        """Get miner version info.

        <details>
            <summary>Expand</summary>

        Returns:
            Miner version information.
        </details>
        """
        return await self.send_command("version")
