#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from pyasic.API import BaseMinerAPI


class BOSMinerAPI(BaseMinerAPI):
    """An abstraction of the BOSMiner API.

    Each method corresponds to an API command in BOSMiner.

    [BOSMiner API documentation](https://docs.braiins.com/os/plus-en/Development/1_api.html)

    This class abstracts use of the BOSMiner API, as well as the
    methods for sending commands to it.  The `self.send_command()`
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.

    Parameters:
        ip: The IP of the miner to reference the API on.
        port: The port to reference the API on.  Default is 4028.
    """

    def __init__(self, ip: str, port: int = 4028):
        super().__init__(ip, port)

    async def asccount(self) -> dict:
        """Get data on the number of ASC devices and their info.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on all ASC devices.
        </details>
        """
        return await self.send_command("asccount")

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

    async def edevs(self, old: bool = False) -> dict:
        """Get data on each PGA/ASC with their details, ignoring blacklisted and zombie devices.
        <details>
            <summary>Expand</summary>

        Parameters:
            old: Include zombie devices that became zombies less than 'old' seconds ago

        Returns:
            Data on each PGA/ASC with their details.
        </details>
        """
        if old:
            return await self.send_command("edevs", parameters="old")
        else:
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

    async def summary(self) -> dict:
        """Get the status summary of the miner.

        <details>
            <summary>Expand</summary>

        Returns:
            The status summary of the miner.
        </details>
        """
        return await self.send_command("summary")

    async def stats(self) -> dict:
        """Get stats of each device/pool with more than 1 getwork.

        <details>
            <summary>Expand</summary>

        Returns:
            Stats of each device/pool with more than 1 getwork.
        </details>
        """
        return await self.send_command("stats")

    async def version(self) -> dict:
        """Get miner version info.

        <details>
            <summary>Expand</summary>

        Returns:
            Miner version information.
        </details>
        """
        return await self.send_command("version")

    async def estats(self, old: bool = False) -> dict:
        """Get stats of each device/pool with more than 1 getwork, ignoring zombie devices.
        <details>
            <summary>Expand</summary>

        Parameters:
            old: Include zombie devices that became zombies less than 'old' seconds ago.

        Returns:
            Stats of each device/pool with more than 1 getwork, ignoring zombie devices.
        </details>
        """
        if old:
            return await self.send_command("estats", parameters=old)
        else:
            return await self.send_command("estats")

    async def check(self, command: str) -> dict:
        """Check if the command command exists in BOSMiner.
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

    async def lcd(self) -> dict:
        """Get a general all-in-one status summary of the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            An all-in-one status summary of the miner.
        </details>
        """
        return await self.send_command("lcd")

    async def fans(self) -> dict:
        """Get fan data.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the fans of the miner.
        </details>
        """
        return await self.send_command("fans")

    async def tempctrl(self) -> dict:
        """Get temperature control data.
        <details>
            <summary>Expand</summary>

        Returns:
            Data about the temp control settings of the miner.
        </details>
        """
        return await self.send_command("tempctrl")

    async def temps(self) -> dict:
        """Get temperature data.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the temps of the miner.
        </details>
        """
        return await self.send_command("temps")

    async def tunerstatus(self) -> dict:
        """Get tuner status data
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the status of autotuning.
        </details>
        """
        return await self.send_command("tunerstatus")

    async def pause(self) -> dict:
        """Pause mining.
        <details>
            <summary>Expand</summary>

        Returns:
            Confirmation of pausing mining.
        </details>
        """
        return await self.send_command("pause")

    async def resume(self) -> dict:
        """Resume mining.
        <details>
            <summary>Expand</summary>

        Returns:
            Confirmation of resuming mining.
        </details>
        """
        return await self.send_command("resume")
