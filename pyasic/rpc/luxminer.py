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
from typing import Literal

from pyasic.rpc.base import BaseMinerRPCAPI


class LUXMinerRPCAPI(BaseMinerRPCAPI):
    """An abstraction of the LUXMiner API.

    Each method corresponds to an API command in LUXMiner.

    [LUXMiner API documentation](https://docs.firmware.luxor.tech/API/intro)

    This class abstracts use of the LUXMiner API, as well as the
    methods for sending commands to it.  The `self.send_command()`
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.
    """

    async def addgroup(self, name: str, quota: int) -> dict:
        """Add a pool group.
        <details>
            <summary>Expand</summary>

        Parameters:
            name: The group name.
            quota: The group quota.

        Returns:
            Confirmation of adding a pool group.
        </details>
        """
        return await self.send_command("addgroup", parameters=f"{name},{quota}")

    async def addpool(
        self, url: str, user: str, pwd: str = "", group_id: str = None
    ) -> dict:
        """Add a pool.
        <details>
            <summary>Expand</summary>

        Parameters:
            url: The pool url.
            user: The pool username.
            pwd: The pool password.
            group_id: The group ID to use.

        Returns:
            Confirmation of adding a pool.
        </details>
        """
        pool_data = [url, user, pwd]
        if group_id is not None:
            pool_data.append(group_id)
        return await self.send_command("addpool", parameters=",".join(pool_data))

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

    async def curtail(self, session_id: str) -> dict:
        """Put the miner into sleep mode.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.

        Returns:
            A confirmation of putting the miner to sleep.
        </details>
        """
        return await self.send_command("curtail", parameters=session_id)

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

    async def disablepool(self, n: int) -> dict:
        """Disable a pool.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: Pool to disable.

        Returns:
            A confirmation of diabling the pool.
        </details>
        """
        return await self.send_command("disablepool", parameters=n)

    async def edevs(self) -> dict:
        """Alias for devs"""
        return await self.devs()

    async def enablepool(self, n: int) -> dict:
        """Enable pool n.
        <details>
            <summary>Expand</summary>

        Parameters:
            n: The pool to enable.

        Returns:
            A confirmation of enabling pool n.
        </details>
        """
        return await self.send_command("enablepool", parameters=n)

    async def estats(self) -> dict:
        """Alias for stats"""
        return await self.stats()

    async def fans(self) -> dict:
        """Get fan data.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the fans of the miner.
        </details>
        """
        return await self.send_command("fans")

    async def fanset(self, session_id: str, speed: int, min_fans: int = None) -> dict:
        """Set fan control.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            speed: The fan speed to set.  Use -1 to set automatically.
            min_fans: The minimum number of fans to use. Optional.

        Returns:
            A confirmation of setting fan control values.
        </details>
        """
        fanset_data = [str(session_id), str(speed)]
        if min_fans is not None:
            fanset_data.append(str(min_fans))
        return await self.send_command("fanset", parameters=",".join(fanset_data))

    async def frequencyget(self, board_n: int, chip_n: int = None) -> dict:
        """Get frequency data for a board and chips.
        <details>
            <summary>Expand</summary>

        Parameters:
            board_n: The board number to get frequency info from.
            chip_n: The chip number to get frequency info from.  Optional.

        Returns:
            Board and/or chip frequency values.
        </details>
        """
        frequencyget_data = [str(board_n)]
        if chip_n is not None:
            frequencyget_data.append(str(chip_n))
        return await self.send_command(
            "frequencyget", parameters=",".join(frequencyget_data)
        )

    async def frequencyset(self, session_id: str, board_n: int, freq: int) -> dict:
        """Set frequency.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            board_n: The board number to set frequency on.
            freq: The frequency to set.

        Returns:
            A confirmation of setting frequency values.
        </details>
        """
        return await self.send_command(
            "frequencyset", parameters=f"{session_id},{board_n},{freq}"
        )

    async def frequencystop(self, session_id: str, board_n: int) -> dict:
        """Stop set frequency.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            board_n: The board number to set frequency on.

        Returns:
            A confirmation of stopping frequencyset value.
        </details>
        """
        return await self.send_command(
            "frequencystop", parameters=f"{session_id},{board_n}"
        )

    async def groupquota(self, group_n: int, quota: int) -> dict:
        """Set a group's quota.
        <details>
            <summary>Expand</summary>

        Parameters:
            group_n: The group number to set quota on.
            quota: The quota to use.

        Returns:
            A confirmation of setting quota value.
        </details>
        """
        return await self.send_command("groupquota", parameters=f"{group_n},{quota}")

    async def groups(self) -> dict:
        """Get pool group data.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the pool groups on the miner.
        </details>
        """
        return await self.send_command("groups")

    async def healthchipget(self, board_n: int, chip_n: int = None) -> dict:
        """Get chip health.
        <details>
            <summary>Expand</summary>

        Parameters:
            board_n: The board number to get chip health of.
            chip_n: The chip number to get chip health of.  Optional.

        Returns:
            Chip health data.
        </details>
        """
        healthchipget_data = [str(board_n)]
        if chip_n is not None:
            healthchipget_data.append(str(chip_n))
        return await self.send_command(
            "healthchipget", parameters=",".join(healthchipget_data)
        )

    async def healthchipset(
        self, session_id: str, board_n: int, chip_n: int = None
    ) -> dict:
        """Select the next chip to have its health checked.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            board_n: The board number to next get chip health of.
            chip_n: The chip number to next get chip health of.  Optional.

        Returns:
            Confirmation of selecting the next health check chip.
        </details>
        """
        healthchipset_data = [session_id, str(board_n)]
        if chip_n is not None:
            healthchipset_data.append(str(chip_n))
        return await self.send_command(
            "healthchipset", parameters=",".join(healthchipset_data)
        )

    async def healthctrl(self) -> dict:
        """Get health check config.
        <details>
            <summary>Expand</summary>

        Returns:
            Health check config.
        </details>
        """
        return await self.send_command("healthctrl")

    async def healthctrlset(
        self, session_id: str, num_readings: int, amplified_factor: float
    ) -> dict:
        """Set health control config.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            num_readings: The minimum number of readings for evaluation.
            amplified_factor: Performance factor of the evaluation.

        Returns:
            A confirmation of setting health control config.
        </details>
        """
        return await self.send_command(
            "healthctrlset",
            parameters=f"{session_id},{num_readings},{amplified_factor}",
        )

    async def kill(self) -> dict:
        """Forced session kill.  Use logoff instead.
        <details>
            <summary>Expand</summary>

        Returns:
            A confirmation of killing the active session.
        </details>
        """
        return await self.send_command("kill")

    async def lcd(self) -> dict:
        """Get a general all-in-one status summary of the miner.  Always zeros on LUXMiner.
        <details>
            <summary>Expand</summary>

        Returns:
            An all-in-one status summary of the miner.
        </details>
        """
        return await self.send_command("lcd")

    async def ledset(
        self,
        session_id: str,
        color: Literal["red"],
        state: Literal["on", "off", "blink"],
    ) -> dict:
        """Set led.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            color: The color LED to set.  Can be "red".
            state: The state to set the LED to.  Can be "on", "off", or "blink".

        Returns:
            A confirmation of setting LED.
        </details>
        """
        return await self.send_command(
            "ledset", parameters=f"{session_id},{color},{state}"
        )

    async def limits(self) -> dict:
        """Get max and min values of config parameters.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on max and min values of config parameters.
        </details>
        """
        return await self.send_command("limits")

    async def logoff(self, session_id: str) -> dict:
        """Log off of a session.  Requires a session id from an active session.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.

        Returns:
            Confirmation of logging off a session.
        </details>
        """
        return await self.send_command("logoff", parameters=session_id)

    async def logon(self) -> dict:
        """Get or create a session.
        <details>
            <summary>Expand</summary>

        Returns:
            The Session ID to be used.
        </details>
        """
        return await self.send_command("logon")

    async def pools(self) -> dict:
        """Get pool information.

        <details>
            <summary>Expand</summary>

        Returns:
            Miner pool information.
        </details>
        """
        return await self.send_command("pools")

    async def power(self) -> dict:
        """Get the estimated power usage in watts.
        <details>
            <summary>Expand</summary>

        Returns:
            Estimated power usage in watts.
        </details>
        """
        return await self.send_command("power")

    async def profiles(self) -> dict:
        """Get the available profiles.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on available profiles.
        </details>
        """
        return await self.send_command("profiles")

    async def profileset(self, session_id: str, board_n: int, profile: str) -> dict:
        """Set active profile for a board.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            board_n: The board to set the profile on.
            profile: The profile name to use.

        Returns:
            A confirmation of setting the profile on board_n.
        </details>
        """
        return await self.send_command(
            "profileset", parameters=f"{session_id},{board_n},{profile}"
        )

    async def reboot(self, session_id: str, board_n: int, delay_s: int = None) -> dict:
        """Reboot a board.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            board_n: The board to reboot.
            delay_s: The number of seconds to delay until startup.  If it is 0, the board will just stop.  Optional.

        Returns:
            A confirmation of rebooting board_n.
        </details>
        """
        reboot_data = [session_id, str(board_n)]
        if delay_s is not None:
            reboot_data.append(str(delay_s))
        return await self.send_command("reboot", parameters=",".join(reboot_data))

    async def rebootdevice(self, session_id: str) -> dict:
        """Reboot the miner.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.

        Returns:
            A confirmation of rebooting the miner.
        </details>
        """
        return await self.send_command("rebootdevice", parameters=session_id)

    async def removegroup(self, group_id: str) -> dict:
        """Remove a pool group.
        <details>
            <summary>Expand</summary>

        Parameters:
            group_id: Group id to remove.

        Returns:
            A confirmation of removing the pool group.
        </details>
        """
        return await self.send_command("removegroup", parameters=group_id)

    async def resetminer(self, session_id: str) -> dict:
        """Restart the mining process.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.

        Returns:
            A confirmation of restarting the mining process.
        </details>
        """
        return await self.send_command("resetminer", parameters=session_id)

    async def removepool(self, pool_id: int) -> dict:
        """Remove a pool.
        <details>
            <summary>Expand</summary>

        Parameters:
            pool_id: Pool to remove.

        Returns:
            A confirmation of removing the pool.
        </details>
        """
        return await self.send_command("removepool", parameters=str(pool_id))

    async def session(self) -> dict:
        """Get the current session.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the current session.
        </details>
        """
        return await self.send_command("session")

    async def tempctrlset(self, target: int, hot: int, dangerous: int) -> dict:
        """Set temp control values.
        <details>
            <summary>Expand</summary>

        Parameters:
            target: Target temp.
            hot: Hot temp.
            dangerous: Dangerous temp.

        Returns:
            A confirmation of setting the temp control config.
        </details>
        """
        return await self.send_command(
            "tempctrlset", parameters=f"{target},{hot},{dangerous}"
        )

    async def stats(self) -> dict:
        """Get stats of each device/pool with more than 1 getwork.

        <details>
            <summary>Expand</summary>

        Returns:
            Stats of each device/pool with more than 1 getwork.
        </details>
        """
        return await self.send_command("stats")

    async def summary(self) -> dict:
        """Get the status summary of the miner.

        <details>
            <summary>Expand</summary>

        Returns:
            The status summary of the miner.
        </details>
        """
        return await self.send_command("summary")

    async def switchpool(self, pool_id: int) -> dict:
        """Switch to a pool.
        <details>
            <summary>Expand</summary>

        Parameters:
            pool_id: Pool to switch to.

        Returns:
            A confirmation of switching to the pool.
        </details>
        """
        return await self.send_command("switchpool", parameters=str(pool_id))

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

    async def version(self) -> dict:
        """Get miner version info.

        <details>
            <summary>Expand</summary>

        Returns:
            Miner version information.
        </details>
        """
        return await self.send_command("version")

    async def voltageget(self, board_n: int) -> dict:
        """Get voltage data for a board.
        <details>
            <summary>Expand</summary>

        Parameters:
            board_n: The board number to get voltage info from.

        Returns:
            Board voltage values.
        </details>
        """
        return await self.send_command("frequencyget", parameters=str(board_n))

    async def voltageset(self, session_id: str, board_n: int, voltage: float) -> dict:
        """Set voltage values.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.
            board_n: The board to set the voltage on.
            voltage: The voltage to use.

        Returns:
            A confirmation of setting the voltage.
        </details>
        """
        return await self.send_command(
            "voltageset", parameters=f"{session_id},{board_n},{voltage}"
        )

    async def wakeup(self, session_id: str) -> dict:
        """Take the miner out of sleep mode.  Requires a session_id from logon.
        <details>
            <summary>Expand</summary>

        Parameters:
            session_id: Session id from the logon command.

        Returns:
            A confirmation of resuming mining.
        </details>
        """
        return await self.send_command("wakeup", parameters=session_id)
