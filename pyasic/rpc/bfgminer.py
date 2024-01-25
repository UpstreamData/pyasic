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

from pyasic.rpc.cgminer import CGMinerRPCAPI


class BFGMinerRPCAPI(CGMinerRPCAPI):
    """An abstraction of the BFGMiner API.

    Each method corresponds to an API command in BFGMiner.

    [BFGMiner API documentation](https://github.com/luke-jr/bfgminer/blob/bfgminer/README.RPC)

    This class abstracts use of the BFGMiner API, as well as the
    methods for sending commands to it.  The self.send_command()
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.
    """

    async def procs(self) -> dict:
        """Get data on each processor with their details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on each processor with their details.
        </details>
        """
        return await self.send_command("procs")

    async def devscan(self, info: str = "") -> dict:
        """Get data on each processor with their details.
        <details>
            <summary>Expand</summary>

        Parameters:
            info: Info to scan for device by.

        Returns:
            Data on each processor with their details.
        </details>
        """
        return await self.send_command("devscan", parameters=info)

    async def proc(self, n: int = 0) -> dict:
        """Get data processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to get data on.

        Returns:
            Data on processor n.
        </details>
        """
        return await self.send_command("proc", parameters=n)

    async def proccount(self) -> dict:
        """Get data fon all processors.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the processors connected.
        </details>
        """
        return await self.send_command("proccount")

    async def pgarestart(self, n: int) -> dict:
        """Restart PGA n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The PGA to restart.

        Returns:
            A confirmation of restarting PGA n.
        </details>
        """
        return await self.send_command("pgadisable", parameters=n)

    async def procenable(self, n: int) -> dict:
        """Enable processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to enable.

        Returns:
            A confirmation of enabling processor n.
        </details>
        """
        return await self.send_command("procenable", parameters=n)

    async def procdisable(self, n: int) -> dict:
        """Disable processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to disable.

        Returns:
            A confirmation of disabling processor n.
        </details>
        """
        return await self.send_command("procdisable", parameters=n)

    async def procrestart(self, n: int) -> dict:
        """Restart processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to restart.

        Returns:
            A confirmation of restarting processor n.
        </details>
        """
        return await self.send_command("procdisable", parameters=n)

    async def procidentify(self, n: int) -> dict:
        """Identify processor n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The processor to identify.

        Returns:
            A confirmation of identifying processor n.
        </details>
        """
        return await self.send_command("procidentify", parameters=n)

    async def procset(self, n: int, opt: str, val: int = None) -> dict:
        """Set processor option opt to val on processor n.
        <details>
            <summary>Expand</summary>

        Options:
        ```
            MMQ -
                opt: clock
                val: 2 - 250 (multiple of 2)
            XBS -
                opt: clock
                val: 2 - 250 (multiple of 2)
        ```

        Parameters:
            n: The processor to set the options on.
            opt: The option to set. Setting this to 'help' returns a help message.
            val: The value to set the option to.

        Returns:
            Confirmation of setting processor n with opt[,val].
        </details>
        """
        if val:
            return await self.send_command("procset", parameters=f"{n},{opt},{val}")
        else:
            return await self.send_command("procset", parameters=f"{n},{opt}")
