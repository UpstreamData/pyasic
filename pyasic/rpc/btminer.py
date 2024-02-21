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

import asyncio
import base64
import binascii
import datetime
import hashlib
import json
import logging
import re
from typing import Literal, Union

import httpx
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from passlib.handlers.md5_crypt import md5_crypt

from pyasic import settings
from pyasic.errors import APIError
from pyasic.misc import api_min_version, validate_command_output
from pyasic.rpc.base import BaseMinerRPCAPI

### IMPORTANT ###
# you need to change the password of the miners using the Whatsminer
# tool, then you can set them back to admin with this tool, but they
# must be changed to something else and set back to admin with this
# or the privileged API will not work using admin as the password.  If
# you change the password, you can pass that to this class as pwd,
# or add it as the Whatsminer_pwd in the settings.toml file.

PrePowerOnMessage = Union[
    Literal["wait for adjust temp"],
    Literal["adjust complete"],
    Literal["adjust continue"],
]


def _crypt(word: str, salt: str) -> str:
    r"""Encrypts a word with a salt, using a standard salt format.

    Encrypts a word using a salt with the format
    \s*\$(\d+)\$([\w\./]*)\$.  If this format is not used, a
    ValueError is raised.

    Parameters:
        word: The word to be encrypted.
        salt: The salt to encrypt the word.

    Returns:
        An MD5 hash of the word with the salt.
    """
    # compile a standard format for the salt
    standard_salt = re.compile(r"\s*\$(\d+)\$([\w\./]*)\$")
    # check if the salt matches
    match = standard_salt.match(salt)
    # if the matching fails, the salt is incorrect
    if not match:
        raise ValueError("Salt format is not correct.")
    # save the matched salt in a new variable
    new_salt = match.group(2)
    # encrypt the word with the salt using md5
    result = md5_crypt.hash(word, salt=new_salt)
    return result


def _add_to_16(string: str) -> bytes:
    """Add null bytes to a string until the length is a multiple 16

    Parameters:
        string: The string to lengthen to a multiple of 16 and encode.

    Returns:
        The input string as bytes with a multiple of 16 as the length.
    """
    while len(string) % 16 != 0:
        string += "\0"
    return str.encode(string)  # return bytes


def parse_btminer_priviledge_data(token_data: dict, data: dict) -> dict:
    """Parses data returned from the BTMiner privileged API.

    Parses data from the BTMiner privileged API using the token
    from the API in an AES format.

    Parameters:
        token_data: The token information from self.get_token().
        data: The data to parse, returned from the API.

    Returns:
        A decoded dict version of the privileged command output.
    """
    # get the encoded data from the dict
    enc_data = data["enc"]
    # get the aes key from the token data
    aeskey = hashlib.sha256(token_data["host_passwd_md5"].encode()).hexdigest()
    # unhexlify the aes key
    aeskey = binascii.unhexlify(aeskey.encode())
    # create the required decryptor
    aes = Cipher(algorithms.AES(aeskey), modes.ECB())
    decryptor = aes.decryptor()
    # decode the message with the decryptor
    ret_msg = json.loads(
        decryptor.update(base64.decodebytes(bytes(enc_data, encoding="utf8")))
        .rstrip(b"\0")
        .decode("utf8")
    )
    return ret_msg


def create_privileged_cmd(token_data: dict, command: dict) -> bytes:
    """Create a privileged command to send to the BTMiner API.

    Creates a privileged command using the token from the API and the
    command as a dict of {'command': cmd}, with cmd being any command
    that the miner API accepts.

    Parameters:
        token_data: The token information from self.get_token().
        command: The command to turn into a privileged command.

    Returns:
        The encrypted privileged command to be sent to the miner.
    """
    logging.debug(f"(Create Prilileged Command) - Creating Privileged Command")
    # add token to command
    command["token"] = token_data["host_sign"]
    # encode host_passwd data and get hexdigest
    aeskey = hashlib.sha256(token_data["host_passwd_md5"].encode()).hexdigest()
    # unhexlify the encoded host_passwd
    aeskey = binascii.unhexlify(aeskey.encode())
    # create a new AES key
    aes = Cipher(algorithms.AES(aeskey), modes.ECB())
    encryptor = aes.encryptor()
    # dump the command to json
    api_json_str = json.dumps(command)
    # encode the json command with the aes key
    api_json_str_enc = (
        base64.encodebytes(encryptor.update(_add_to_16(api_json_str)))
        .decode("utf-8")
        .replace("\n", "")
    )
    # label the data as being encoded
    data_enc = {"enc": 1, "data": api_json_str_enc}
    # dump the labeled data to json
    api_packet_str = json.dumps(data_enc)
    return api_packet_str.encode("utf-8")


class BTMinerRPCAPI(BaseMinerRPCAPI):
    """An abstraction of the API for MicroBT Whatsminers, BTMiner.

    Each method corresponds to an API command in BMMiner.

    This class abstracts use of the BTMiner API, as well as the
    methods for sending commands to it.  The `self.send_command()`
    function handles sending a command to the miner asynchronously, and
    as such is the base for many of the functions in this class, which
    rely on it to send the command for them.

    All privileged commands for BTMiner's API require that you change
    the password of the miners using the Whatsminer tool, and it can be
    changed back to admin with this tool after.  Set the new password
    either by passing it to the __init__ method, or changing it in
    settings.toml.

    Additionally, the API commands for the privileged API must be
    encoded using a token from the miner, all privileged commands do
    this automatically for you and will decode the output to look like
    a normal output from a miner API.
    """

    def __init__(self, ip: str, port: int = 4028, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, port, api_ver)
        self.pwd = settings.get("default_whatsminer_rpc_password", "admin")
        self.token = None

    async def multicommand(self, *commands: str, allow_warning: bool = True) -> dict:
        """Creates and sends multiple commands as one command to the miner.

        Parameters:
            *commands: The commands to send as a multicommand to the miner.
            allow_warning: A boolean to supress APIWarnings.
        """
        # make sure we can actually run each command, otherwise they will fail
        commands = self._check_commands(*commands)
        # standard multicommand format is "command1+command2"
        # commands starting with "get_" and the "status" command aren't supported, but we can fake that

        split_commands = []

        for command in list(commands):
            if command.startswith("get_") or command == "status":
                commands.remove(command)
                # send seperately and append later
                split_commands.append(command)

        command = "+".join(commands)

        tasks = []
        if len(split_commands) > 0:
            tasks.append(
                asyncio.create_task(
                    self._send_split_multicommand(
                        *split_commands, allow_warning=allow_warning
                    )
                )
            )
        tasks.append(
            asyncio.create_task(self.send_command(command, allow_warning=allow_warning))
        )

        try:
            all_data = await asyncio.gather(*tasks)
        except APIError:
            return {}

        data = {}
        for item in all_data:
            data.update(item)

        data["multicommand"] = True
        return data

    async def send_privileged_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        timeout: int = 10,
        **kwargs,
    ) -> dict:
        try:
            return await self._send_privileged_command(
                command=command, ignore_errors=ignore_errors, timeout=timeout, **kwargs
            )
        except APIError as e:
            if not e.message == "can't access write cmd":
                raise
        try:
            await self.open_api()
        except Exception as e:
            raise APIError("Failed to open whatsminer API.") from e
        return await self._send_privileged_command(
            command=command, ignore_errors=ignore_errors, timeout=timeout, **kwargs
        )

    async def _send_privileged_command(
        self,
        command: Union[str, bytes],
        ignore_errors: bool = False,
        timeout: int = 10,
        **kwargs,
    ) -> dict:
        logging.debug(
            f"{self} - (Send Privileged Command) - {command} " + f"with args {kwargs}"
            if len(kwargs) > 0
            else ""
        )
        command = {"cmd": command, **kwargs}

        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)

        logging.debug(f"{self} - (Send Privileged Command) - Sending")
        try:
            data = await self._send_bytes(enc_command, timeout=timeout)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            if ignore_errors:
                return {}
            raise APIError("No data was returned from the API.")

        if not data:
            if ignore_errors:
                return {}
            raise APIError("No data was returned from the API.")
        data = self._load_api_data(data)

        try:
            data = parse_btminer_priviledge_data(self.token, data)
        except Exception as e:
            logging.info(f"{str(self.ip)}: {e}")

        if not ignore_errors:
            # if it fails to validate, it is likely an error
            validation = validate_command_output(data)
            if not validation[0]:
                raise APIError(validation[1])

        # return the parsed json as a dict
        return data

    async def get_token(self) -> dict:
        """Gets token information from the API.
        <details>
            <summary>Expand</summary>

        Returns:
            An encoded token and md5 password, which are used for the privileged API.
        </details>
        """
        logging.debug(f"{self} - (Get Token) - Getting token")
        if self.token:
            if self.token["timestamp"] > datetime.datetime.now() - datetime.timedelta(
                minutes=30
            ):
                return self.token

        # get the token
        data = await self.send_command("get_token")

        # encrypt the admin password with the salt
        pwd = _crypt(self.pwd, "$1$" + data["Msg"]["salt"] + "$")
        pwd = pwd.split("$")

        # take the 4th item from the pwd split
        host_passwd_md5 = pwd[3]

        # encrypt the pwd with the time and new salt
        tmp = _crypt(pwd[3] + data["Msg"]["time"], "$1$" + data["Msg"]["newsalt"] + "$")
        tmp = tmp.split("$")

        # take the 4th item from the encrypted pwd split
        host_sign = tmp[3]

        # set the current token
        self.token = {
            "host_sign": host_sign,
            "host_passwd_md5": host_passwd_md5,
            "timestamp": datetime.datetime.now(),
        }
        logging.debug(f"{self} - (Get Token) - Gathered token data: {self.token}")
        return self.token

    async def open_api(self):
        async with httpx.AsyncClient() as c:
            stage1_req = (
                await c.post(
                    "https://wmt.pyasic.org/v1/stage1",
                    json={"ip": str(self.ip)},
                    follow_redirects=True,
                )
            ).json()
            stage1_res = binascii.hexlify(
                await self._send_bytes(binascii.unhexlify(stage1_req), port=8889)
            )
            stage2_req = (
                await c.post(
                    "https://wmt.pyasic.org/v1/stage2",
                    json={
                        "ip": str(self.ip),
                        "stage1_result": stage1_res.decode("utf-8"),
                    },
                )
            ).json()
        for command in stage2_req:
            try:
                await self._send_bytes(
                    binascii.unhexlify(command), timeout=3, port=8889
                )
            except asyncio.TimeoutError:
                pass
        return True

    #### PRIVILEGED COMMANDS ####
    # Please read the top of this file to learn
    # how to configure the Whatsminer API to
    # use these commands.

    async def update_pools(
        self,
        pool_1: str,
        worker_1: str,
        passwd_1: str,
        pool_2: str = None,
        worker_2: str = None,
        passwd_2: str = None,
        pool_3: str = None,
        worker_3: str = None,
        passwd_3: str = None,
    ) -> dict:
        """Update the pools of the miner using the API.
        <details>
            <summary>Expand</summary>

        Update the pools of the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            pool_1: The URL to update pool 1 to.
            worker_1: The worker name for pool 1 to update to.
            passwd_1: The password for pool 1 to update to.
            pool_2: The URL to update pool 2 to.
            worker_2: The worker name for pool 2 to update to.
            passwd_2: The password for pool 2 to update to.
            pool_3: The URL to update pool 3 to.
            worker_3: The worker name for pool 3 to update to.
            passwd_3: The password for pool 3 to update to.

        Returns:
            A dict from the API to confirm the pools were updated.
        </details>
        """
        return await self.send_privileged_command(
            "update_pools",
            pool1=pool_1,
            worker1=worker_1,
            passwd1=passwd_1,
            pool2=pool_2,
            worker2=worker_2,
            passwd2=passwd_2,
            pool3=pool_3,
            worker3=worker_3,
            passwd3=passwd_3,
        )

    async def restart(self) -> dict:
        """Restart BTMiner using the API.
        <details>
            <summary>Expand</summary>

        Restart BTMiner using the API, only works after changing
        the password of the miner using the Whatsminer tool.

        Returns:
            A reply informing of the restart.
        </details>
        """
        return await self.send_privileged_command("restart_btminer")

    async def power_off(self, respbefore: bool = True) -> dict:
        """Power off the miner using the API.
        <details>
            <summary>Expand</summary>

        Power off the miner using the API, only works after changing
        the password of the miner using the Whatsminer tool.

        Parameters:
            respbefore: Whether to respond before powering off.
        Returns:
            A reply informing of the status of powering off.
        </details>
        """
        if respbefore:
            return await self.send_privileged_command("power_off", respbefore="true")
        return await self.send_privileged_command("power_off", respbefore="false")

    async def power_on(self) -> dict:
        """Power on the miner using the API.
        <details>
            <summary>Expand</summary>

        Power on the miner using the API, only works after changing
        the password of the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of powering on.
        </details>
        """
        return await self.send_privileged_command("power_on")

    async def reset_led(self) -> dict:
        """Reset the LED on the miner using the API.
        <details>
            <summary>Expand</summary>

        Reset the LED on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of resetting the LED.
        </details>
        """
        return await self.set_led(auto=True)

    async def set_led(
        self,
        auto: bool = True,
        color: str = "red",
        period: int = 60,
        duration: int = 20,
        start: int = 0,
    ) -> dict:
        """Set the LED on the miner using the API.
        <details>
            <summary>Expand</summary>

        Set the LED on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            auto: Whether or not to reset the LED to auto mode.
            color: The LED color to set, either 'red' or 'green'.
            period: The flash cycle in ms.
            duration: LED on time in the cycle in ms.
            start: LED on time offset in the cycle in ms.
        Returns:
            A reply informing of the status of setting the LED.
        </details>
        """
        if auto:
            return await self.send_privileged_command("set_led", param="auto")
        return await self.send_privileged_command(
            "set_led", color=color, period=period, duration=duration, start=start
        )

    async def set_low_power(self) -> dict:
        """Set low power mode on the miner using the API.
        <details>
            <summary>Expand</summary>

        Set low power mode on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of setting low power mode.
        </details>
        """
        return await self.send_privileged_command("set_low_power")

    async def set_high_power(self) -> dict:
        """Set low power mode on the miner using the API.
        <details>
            <summary>Expand</summary>

        Set low power mode on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of setting low power mode.
        </details>
        """
        return await self.send_privileged_command("set_high_power")

    async def set_normal_power(self) -> dict:
        """Set low power mode on the miner using the API.
        <details>
            <summary>Expand</summary>

        Set low power mode on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of setting low power mode.
        </details>
        """
        return await self.send_privileged_command("set_normal_power")

    async def update_firmware(self):  # noqa - static
        """Not implemented."""
        # to be determined if this will be added later
        # requires a file stream in bytes
        return NotImplementedError

    async def reboot(self, timeout: int = 10) -> dict:
        """Reboot the miner using the API.
        <details>
            <summary>Expand</summary>

        Returns:
            A reply informing of the status of the reboot.
        </details>
        """
        try:
            d = await asyncio.wait_for(
                self.send_privileged_command("reboot"), timeout=timeout
            )
        except (asyncio.CancelledError, asyncio.TimeoutError):
            return {}
        else:
            return d

    async def factory_reset(self) -> dict:
        """Reset the miner to factory defaults.
        <details>
            <summary>Expand</summary>

        Returns:
            A reply informing of the status of the reset.
        </details>
        """
        return await self.send_privileged_command("factory_reset")

    async def update_pwd(self, old_pwd: str, new_pwd: str) -> dict:
        """Update the admin user's password.

        <details>
            <summary>Expand</summary>

        Update the admin user's password, only works after changing the
        password of the miner using the Whatsminer tool.  New password
        has a max length of 8 bytes, using letters, numbers, and
        underscores.

        Parameters:
            old_pwd: The old admin password.
            new_pwd: The new password to set.
        Returns:
            A reply informing of the status of setting the password.
        """
        self.pwd = old_pwd
        # check if password length is greater than 8 bytes
        if len(new_pwd.encode("utf-8")) > 8:
            raise APIError(
                f"New password too long, the max length is 8.  "
                f"Password size: {len(new_pwd.encode('utf-8'))}"
            )
        try:
            data = await self.send_privileged_command(
                "update_pwd", old=old_pwd, new=new_pwd
            )
        except APIError as e:
            raise e
        self.pwd = new_pwd
        return data

    async def net_config(
        self,
        ip: str = None,
        mask: str = None,
        gate: str = None,
        dns: str = None,
        host: str = None,
        dhcp: bool = True,
    ):
        if dhcp:
            return await self.send_privileged_command("net_config", param="dhcp")
        if None in [ip, mask, gate, dns, host]:
            raise APIError("Incorrect parameters.")
        return await self.send_privileged_command(
            "net_config", ip=ip, mask=mask, gate=gate, dns=dns, host=host
        )

    async def set_target_freq(self, percent: int) -> dict:
        """Update the target frequency.

        <details>
            <summary>Expand</summary>

        Update the target frequency, only works after changing the
        password of the miner using the Whatsminer tool. The new
        frequency must be between -10% and 100%.

        Parameters:
            percent: The frequency % to set.
        Returns:
            A reply informing of the status of setting the frequency.
        </details>
        """
        if not -100 < percent < 100:
            raise APIError(
                f"Frequency % is outside of the allowed "
                f"range.  Please set a % between -100 and "
                f"100"
            )
        return await self.send_privileged_command(
            "set_target_freq", percent=str(percent)
        )

    async def enable_fast_boot(self) -> dict:
        """Turn on fast boot.

        <details>
            <summary>Expand</summary>

        Turn on fast boot, only works after changing the password of
        the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of enabling fast boot.
        </details>
        """
        return await self.send_privileged_command("enable_btminer_fast_boot")

    async def disable_fast_boot(self) -> dict:
        """Turn off fast boot.

        <details>
            <summary>Expand</summary>

        Turn off fast boot, only works after changing the password of
        the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of disabling fast boot.
        </details>
        """
        return await self.send_privileged_command("disable_btminer_fast_boot")

    async def enable_web_pools(self) -> dict:
        """Turn on web pool updates.

        <details>
            <summary>Expand</summary>

        Turn on web pool updates, only works after changing the
        password of the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of enabling web pools.
        </details>
        """
        return await self.send_privileged_command("enable_web_pools")

    async def disable_web_pools(self) -> dict:
        """Turn off web pool updates.

        <details>
            <summary>Expand</summary>

        Turn off web pool updates, only works after changing the
        password of the miner using the Whatsminer tool.

        Returns:
            A reply informing of the status of disabling web pools.
        </details>
        """
        return await self.send_privileged_command("disable_web_pools")

    async def set_hostname(self, hostname: str) -> dict:
        """Set the hostname of the miner.

        <details>
            <summary>Expand</summary>

        Set the hostname of the miner, only works after changing the
        password of the miner using the Whatsminer tool.

        Parameters:
            hostname: The new hostname to use.
        Returns:
            A reply informing of the status of setting the hostname.
        </details>
        """
        return await self.send_privileged_command("set_hostname", hostname=hostname)

    async def set_power_pct(self, percent: int) -> dict:
        """Set the power percentage of the miner based on current power.  Used for temporary adjustment.

        <details>
            <summary>Expand</summary>

        Set the power percentage of the miner, only works after changing
        the password of the miner using the Whatsminer tool.

        Parameters:
            percent: The power percentage to set.
        Returns:
            A reply informing of the status of setting the power percentage.
        </details>
        """

        if not 0 < percent < 100:
            raise APIError(
                f"Power PCT % is outside of the allowed "
                f"range.  Please set a % between 0 and "
                f"100"
            )
        return await self.send_privileged_command("set_power_pct", percent=str(percent))

    async def pre_power_on(self, complete: bool, msg: PrePowerOnMessage) -> dict:
        """Configure or check status of pre power on.

        <details>
            <summary>Expand</summary>

        Configure or check status of pre power on, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            complete: check whether pre power on is complete.
            msg: ## the message to check.
                * `wait for adjust temp`
                * `adjust complete`
                * `adjust continue`
        Returns:
            A reply informing of the status of pre power on.
        </details>
        """

        if msg not in ("wait for adjust temp", "adjust complete", "adjust continue"):
            raise APIError(
                "Message is incorrect, please choose one of "
                '["wait for adjust temp", '
                '"adjust complete", '
                '"adjust continue"]'
            )
        if complete:
            return await self.send_privileged_command(
                "pre_power_on", complete="true", msg=msg
            )
        return await self.send_privileged_command(
            "pre_power_on", complete="false", msg=msg
        )

    ### ADDED IN V2.0.5 Whatsminer API ###

    @api_min_version("2.0.5")
    async def set_power_pct_v2(self, percent: int) -> dict:
        """Set the power percentage of the miner based on current power.  Used for temporary adjustment.  Added in API v2.0.5.

        <details>
            <summary>Expand</summary>

        Set the power percentage of the miner, only works after changing
        the password of the miner using the Whatsminer tool.

        Parameters:
            percent: The power percentage to set.
        Returns:
            A reply informing of the status of setting the power percentage.
        </details>
        """

        if not 0 < percent < 100:
            raise APIError(
                f"Power PCT % is outside of the allowed "
                f"range.  Please set a % between 0 and "
                f"100"
            )
        return await self.send_privileged_command(
            "set_power_pct_v2", percent=str(percent)
        )

    @api_min_version("2.0.5")
    async def set_temp_offset(self, temp_offset: int) -> dict:
        """Set the offset of miner hash board target temperature.

        <details>
            <summary>Expand</summary>

        Set the offset of miner hash board target temperature, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            temp_offset: Target temperature offset.
        Returns:
            A reply informing of the status of setting temp offset.
        </details>

        """
        if not -30 < temp_offset < 0:
            raise APIError(
                f"Temp offset is outside of the allowed "
                f"range.  Please set a number between -30 and "
                f"0."
            )

        return await self.send_privileged_command(
            "set_temp_offset", temp_offset=temp_offset
        )

    @api_min_version("2.0.5")
    async def adjust_power_limit(self, power_limit: int) -> dict:
        """Set the upper limit of the miner's power. Cannot be higher than the ordinary power of the machine.

        <details>
            <summary>Expand</summary>

        Set the upper limit of the miner's power, only works after
        changing the password of the miner using the Whatsminer tool.
        The miner will reboot after this is set.

        Parameters:
            power_limit: New power limit.
        Returns:
            A reply informing of the status of setting power limit.
        </details>

        """
        return await self.send_privileged_command(
            "adjust_power_limit", power_limit=str(power_limit)
        )

    @api_min_version("2.0.5")
    async def adjust_upfreq_speed(self, upfreq_speed: int) -> dict:
        """Set the upfreq speed, 0 is the normal speed, 9 is the fastest speed.

        <details>
            <summary>Expand</summary>

        Set the upfreq speed, 0 is the normal speed, 9 is the fastest speed, only works after
        changing the password of the miner using the Whatsminer tool.
        The faster the speed, the greater the final hash rate and power deviation, and the stability
        may be impacted. Fast boot mode cannot be used at the same time.

        Parameters:
            upfreq_speed: New upfreq speed.
        Returns:
            A reply informing of the status of setting upfreq speed.
        </details>
        """
        if not 0 < upfreq_speed < 9:
            raise APIError(
                f"Upfreq speed is outside of the allowed "
                f"range.  Please set a number between 0 (Normal) and "
                f"9 (Fastest)."
            )
        return await self.send_privileged_command(
            "adjust_upfreq_speed", upfreq_speed=upfreq_speed
        )

    @api_min_version("2.0.5")
    async def set_poweroff_cool(self, poweroff_cool: bool) -> dict:
        """Set whether to cool the machine when mining is stopped.

        <details>
            <summary>Expand</summary>

        Set whether to cool the machine when mining is stopped, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            poweroff_cool: Whether to cool the miner during power off mode.
        Returns:
            A reply informing of the status of setting power off cooling mode.
        </details>
        """

        return await self.send_privileged_command(
            "set_poweroff_cool", poweroff_cool=int(poweroff_cool)
        )

    @api_min_version("2.0.5")
    async def set_fan_zero_speed(self, fan_zero_speed: bool) -> dict:
        """Sets whether the fan speed supports the lowest 0 speed.

        <details>
            <summary>Expand</summary>

        Sets whether the fan speed supports the lowest 0 speed, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            fan_zero_speed: Whether the fan is allowed to support 0 speed.
        Returns:
            A reply informing of the status of setting fan minimum speed.
        </details>

        """
        return await self.send_privileged_command(
            "set_fan_zero_speed", fan_zero_speed=int(fan_zero_speed)
        )

    #### END privileged COMMANDS ####

    async def summary(self) -> dict:
        """Get the summary status from the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            Summary status of the miner.
        </details>
        """
        return await self.send_command("summary")

    async def pools(self) -> dict:
        """Get the pool status from the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            Pool status of the miner.
        </details>
        """
        return await self.send_command("pools")

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
        """Get data on each PGA/ASC with their details, ignoring blacklisted and zombie devices.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on each PGA/ASC with their details.
        </details>
        """
        return await self.send_command("edevs")

    async def devdetails(self) -> dict:
        """Get data on all devices with their static details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on all devices with their static details.
        </details>
        """
        return await self.send_command("devdetails")

    async def get_psu(self) -> dict:
        """Get data on the PSU and power information.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the PSU and power information.
        </details>
        """
        return await self.send_command("get_psu")

    async def version(self) -> dict:
        """Get version data for the miner.  Wraps `self.get_version()`.
        <details>
            <summary>Expand</summary>

        Get version data for the miner.  This calls another function,
        self.get_version(), but is named version to stay consistent
        with the other miner APIs.

        Returns:
            Version data for the miner.
        </details>
        """
        return await self.get_version()

    async def get_version(self) -> dict:
        """Get version data for the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            Version data for the miner.
        </details>
        """
        return await self.send_command("get_version")

    async def status(self) -> dict:
        """Get BTMiner status and firmware version.
        <details>
            <summary>Expand</summary>

        Returns:
            BTMiner status and firmware version.
        </details>
        """
        return await self.send_command("status")

    async def get_miner_info(self) -> dict:
        """Get general miner info.
        <details>
            <summary>Expand</summary>

        Returns:
            General miner info.
        </details>
        """
        return await self.send_command("get_miner_info", allow_warning=False)

    @api_min_version("2.0.1")
    async def get_error_code(self) -> dict:
        """Get a list of error codes from the miner.

        <details>
            <summary>Expand</summary>
        Get a list of error codes from the miner.  Replaced `summary` as the location of error codes with API version 2.0.4.

        Returns:
            A list of error codes on the miner.
        </details>
        """
        return await self.send_command("get_error_code", allow_warning=False)
