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
from typing import Literal, Optional, Union

from pyasic import APIError
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_token = None

    async def send_privileged_command(
        self, command: Union[str, bytes], *args, **kwargs
    ) -> dict:
        if self.session_token is None:
            await self.auth()
        return await self.send_command(
            command,
            self.session_token,
            *args,
            **kwargs,
        )

    async def send_command(
        self,
        command: Union[str, bytes],
        *args,
        **kwargs,
    ) -> dict:
        if kwargs.get("parameters") is not None and len(args) == 0:
            return await super().send_command(command, **kwargs)
        return await super().send_command(command, parameters=",".join(args), **kwargs)

    async def auth(self) -> Optional[str]:
        try:
            data = await self.session()
            if not data["SESSION"][0]["SessionID"] == "":
                self.session_token = data["SESSION"][0]["SessionID"]
                return self.session_token
        except APIError:
            pass

        try:
            data = await self.logon()
            self.session_token = data["SESSION"][0]["SessionID"]
            return self.session_token
        except (LookupError, APIError):
            pass

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
        return await self.send_command("addgroup", name, quota)

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
        return await self.send_command("addpool", *pool_data)

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
        return await self.send_command("asc", n)

    async def asccount(self) -> dict:
        """Get data on the number of ASC devices and their info.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on all ASC devices.
        </details>
        """
        return await self.send_command("asccount")

    async def atm(self) -> dict:
        """Get data for Advanced Thermal Management (ATM) configuration.
        <details>
            <summary>Expand</summary>

        Returns:
            A dictionary containing ATM configuration data:
            - ATM: List containing a configuration object with:
                - Enabled: Boolean indicating if ATM is enabled
                - MaxProfile: Maximum frequency profile (e.g., "395MHz")
                - MinProfile: Minimum frequency profile (e.g., "145MHz")
                - PostRampMinutes: Minutes before ATM starts working after ramping
                - StartupMinutes: Minutes before ATM starts working at systm startup
                - TempWindow: Temperature window, before "Hot" in which ATM will change profiles
            - STATUS: List containing a status object with:
                - Code: Status code (e.g., 339)
                - Description: Miner version
                - Msg: Status message "ATM configuration values"
                - STATUS: Status indicator
                - When: Timestamp
        </details>
        """
        return await self.send_command("atm")

    async def atmset(
        self,
        enabled: bool = None,
        startup_minutes: int = None,
        post_ramp_minutes: int = None,
        temp_window: int = None,
        min_profile: str = None,
        max_profile: str = None,
        prevent_oc: bool = None,
    ) -> dict:
        """Sets the ATM configuration.
        <details>
            <summary>Expand</summary>

        Parameters:
            enabled: Enable or disable ATM
            startup_minutes: Minimum time (minutes) before ATM starts at system startup
            post_ramp_minutes: Minimum time (minutes) before ATM starts after ramping
            temp_window: Number of degrees below "Hot" temperature where ATM begins adjusting profiles
            min_profile: Lowest profile to use (e.g. "145MHz", "+1", "-2"). Empty string for unbounded
            max_profile: Highest profile to use (e.g. "395MHz", "+1", "-2")
            prevent_oc: When turning off ATM, revert to default profile if in higher profile

        Returns:
            A dictionary containing status information about the ATM configuration update:
            - STATUS: List containing a status object with:
                - Code: Status code (e.g., 340)
                - Description: Miner version
                - Msg: Confirmation message "Advanced Thermal Management configuration updated"
                - STATUS: Status indicator
                - When: Timestamp
        </details>
        """
        atmset_data = []
        if enabled is not None:
            atmset_data.append(f"enabled={str(enabled).lower()}")
        if startup_minutes is not None:
            atmset_data.append(f"startup_minutes={startup_minutes}")
        if post_ramp_minutes is not None:
            atmset_data.append(f"post_ramp_minutes={post_ramp_minutes}")
        if temp_window is not None:
            atmset_data.append(f"temp_window={temp_window}")
        if min_profile is not None:
            atmset_data.append(f"min_profile={min_profile}")
        if max_profile is not None:
            atmset_data.append(f"max_profile={max_profile}")
        if prevent_oc is not None:
            atmset_data.append(f"prevent_oc={str(prevent_oc).lower()}")
        return await self.send_privileged_command("atmset", *atmset_data)

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
        return await self.send_command("check", command)

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

    async def curtail(self) -> dict:
        """Put the miner into sleep mode.
        <details>
            <summary>Expand</summary>

        Returns:
            A confirmation of putting the miner to sleep.
        </details>
        """
        return await self.send_privileged_command("curtail", "sleep")

    async def sleep(self) -> dict:
        """Put the miner into sleep mode.
        <details>
            <summary>Expand</summary>

        Returns:
            A confirmation of putting the miner to sleep.
        </details>
        """
        return await self.send_privileged_command("curtail", "sleep")

    async def wakeup(self) -> dict:
        """Wake the miner up from sleep mode.
        <details>
            <summary>Expand</summary>

        Returns:
            A confirmation of waking the miner up.
        </details>
        """
        return await self.send_privileged_command("curtail", "wakeup")

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
        return await self.send_command("disablepool", n)

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
        return await self.send_command("enablepool", n)

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

    async def fanset(
        self, speed: int = None, min_fans: int = None, power_off_speed: int = None
    ) -> dict:
        """Set fan control.
        <details>
            <summary>Expand</summary>

        Parameters:
            speed: The fan speed to set.  Use -1 to set automatically.
            min_fans: The minimum number of fans to use. Optional.

        Returns:
            A confirmation of setting fan control values.
        </details>
        """
        fanset_data = []
        if speed is not None:
            fanset_data.append(f"speed={speed}")
        if min_fans is not None:
            fanset_data.append(f"min_fans={min_fans}")
        if power_off_speed is not None:
            fanset_data.append(f"power_off_speed={power_off_speed}")
        return await self.send_privileged_command("fanset", *fanset_data)

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
        return await self.send_command("frequencyget", *frequencyget_data)

    async def frequencyset(self, board_n: int, freq: int) -> dict:
        """Set frequency.
        <details>
            <summary>Expand</summary>

        Parameters:
            board_n: The board number to set frequency on.
            freq: The frequency to set.

        Returns:
            A confirmation of setting frequency values.
        </details>
        """
        return await self.send_privileged_command("frequencyset", board_n, freq)

    async def frequencystop(self, board_n: int) -> dict:
        """Stop set frequency.
        <details>
            <summary>Expand</summary>

        Parameters:
            board_n: The board number to set frequency on.

        Returns:
            A confirmation of stopping frequencyset value.
        </details>
        """
        return await self.send_privileged_command("frequencystop", board_n)

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
        return await self.send_command("groupquota", group_n, quota)

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
        return await self.send_command("healthchipget", *healthchipget_data)

    async def healthchipset(self, board_n: int, chip_n: int = None) -> dict:
        """Select the next chip to have its health checked.
        <details>
            <summary>Expand</summary>

        Parameters:
            board_n: The board number to next get chip health of.
            chip_n: The chip number to next get chip health of.  Optional.

        Returns:
            Confirmation of selecting the next health check chip.
        </details>
        """
        healthchipset_data = [str(board_n)]
        if chip_n is not None:
            healthchipset_data.append(str(chip_n))
        return await self.send_privileged_command("healthchipset", *healthchipset_data)

    async def healthctrl(self) -> dict:
        """Get health check config.
        <details>
            <summary>Expand</summary>

        Returns:
            Health check config.
        </details>
        """
        return await self.send_command("healthctrl")

    async def healthctrlset(self, num_readings: int, amplified_factor: float) -> dict:
        """Set health control config.
        <details>
            <summary>Expand</summary>

        Parameters:
            num_readings: The minimum number of readings for evaluation.
            amplified_factor: Performance factor of the evaluation.

        Returns:
            A confirmation of setting health control config.
        </details>
        """
        return await self.send_privileged_command(
            "healthctrlset", num_readings, amplified_factor
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
        color: Literal["red"],
        state: Literal["on", "off", "blink"],
    ) -> dict:
        """Set led.
        <details>
            <summary>Expand</summary>

        Parameters:
            color: The color LED to set.  Can be "red".
            state: The state to set the LED to.  Can be "on", "off", or "blink".

        Returns:
            A confirmation of setting LED.
        </details>
        """
        return await self.send_privileged_command("ledset", color, state)

    async def limits(self) -> dict:
        """Get max and min values of config parameters.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on max and min values of config parameters.
        </details>
        """
        return await self.send_command("limits")

    async def logoff(self) -> dict:
        """Log off of a session.
        <details>
            <summary>Expand</summary>

        Returns:
            Confirmation of logging off a session.
        </details>
        """
        res = await self.send_privileged_command("logoff")
        self.session_token = None
        return res

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

    async def profileset(self, profile: str) -> dict:
        """Set active profile for the system.
        <details>
            <summary>Expand</summary>

        Parameters:
            profile: The profile name to use.

        Returns:
            A confirmation of setting the profile.
        </details>
        """
        return await self.send_privileged_command("profileset", profile)

    async def reboot(self, board_n: int, delay_s: int = None) -> dict:
        """Reboot a board.
        <details>
            <summary>Expand</summary>

        Parameters:
            board_n: The board to reboot.
            delay_s: The number of seconds to delay until startup.  If it is 0, the board will just stop.  Optional.

        Returns:
            A confirmation of rebooting board_n.
        </details>
        """
        reboot_data = [str(board_n)]
        if delay_s is not None:
            reboot_data.append(str(delay_s))
        return await self.send_privileged_command("reboot", *reboot_data)

    async def rebootdevice(self) -> dict:
        """Reboot the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            A confirmation of rebooting the miner.
        </details>
        """
        return await self.send_privileged_command("rebootdevice")

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

    async def resetminer(self) -> dict:
        """Restart the mining process.
        <details>
            <summary>Expand</summary>

        Returns:
            A confirmation of restarting the mining process.
        </details>
        """
        return await self.send_privileged_command("resetminer")

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

    async def tempctrlset(
        self, target: int = None, hot: int = None, dangerous: int = None
    ) -> dict:
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
            "tempctrlset", target or "", hot or "", dangerous or ""
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
        return await self.send_command("switchpool", pool_id)

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
        return await self.send_command("frequencyget", board_n)

    async def voltageset(self, board_n: int, voltage: float) -> dict:
        """Set voltage values.
        <details>
            <summary>Expand</summary>

        Parameters:
            board_n: The board to set the voltage on.
            voltage: The voltage to use.

        Returns:
            A confirmation of setting the voltage.
        </details>
        """
        return await self.send_privileged_command("voltageset", board_n, voltage)

    async def updaterun(self) -> dict:
        """
        Send the 'updaterun' command to the miner.

        Returns:
            The response from the miner after sending the 'updaterun' command.
        """
        return await self.send_command("updaterun")
