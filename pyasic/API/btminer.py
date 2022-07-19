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

import asyncio
import re
import json
import hashlib
import binascii
import base64
import logging

from passlib.handlers.md5_crypt import md5_crypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from pyasic.API import BaseMinerAPI, APIError
from pyasic.settings import PyasicSettings


### IMPORTANT ###
# you need to change the password of the miners using the Whatsminer
# tool, then you can set them back to admin with this tool, but they
# must be changed to something else and set back to admin with this
# or the privileged API will not work using admin as the password.  If
# you change the password, you can pass that to the this class as pwd,
# or add it as the Whatsminer_pwd in the settings.toml file.


def _crypt(word: str, salt: str) -> str:
    """Encrypts a word with a salt, using a standard salt format.

    Encrypts a word using a salt with the format
    '\s*\$(\d+)\$([\w\./]*)\$'.  If this format is not used, a
    ValueError is raised.

    Parameters:
        word: The word to be encrypted.
        salt: The salt to encrypt the word.

    Returns:
        An MD5 hash of the word with the salt.
    """
    # compile a standard format for the salt
    standard_salt = re.compile("\s*\$(\d+)\$([\w\./]*)\$")
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


def parse_btminer_priviledge_data(token_data: dict, data: dict):
    """Parses data returned from the BTMiner privileged API.

    Parses data from the BTMiner privileged API using the the token
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


class BTMinerAPI(BaseMinerAPI):
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

    Parameters:
        ip: The IP of the miner to reference the API on.
        port: The port to reference the API on.  Default is 4028.
        pwd: The admin password of the miner.  Default is admin.
    """

    def __init__(
        self,
        ip: str,
        port: int = 4028,
        pwd: str = PyasicSettings().global_whatsminer_password,
    ):
        super().__init__(ip, port)
        self.admin_pwd = pwd
        self.current_token = None

    async def send_command(
        self,
        command: str or bytes,
        parameters: str or int or bool = None,
        ignore_errors: bool = False,
        **kwargs,
    ) -> dict:
        # check if command is a string
        # if its bytes its encoded and needs to be sent raw
        if isinstance(command, str):
            # if it is a string, put it into the standard command format
            command = json.dumps({"command": command}).encode("utf-8")
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(self.ip), self.port)
        # handle OSError 121
        except OSError as e:
            if e.winerror == "121":
                print("Semaphore Timeout has Expired.")
            return {}

        # send the command
        writer.write(command)
        await writer.drain()

        # instantiate data
        data = b""

        # loop to receive all the data
        try:
            while True:
                d = await reader.read(4096)
                if not d:
                    break
                data += d
        except Exception as e:
            logging.info(f"{str(self.ip)}: {e}")

        data = self._load_api_data(data)

        # close the connection
        writer.close()
        await writer.wait_closed()

        # check if the returned data is encoded
        if "enc" in data.keys():
            # try to parse the encoded data
            try:
                data = parse_btminer_priviledge_data(self.current_token, data)
            except Exception as e:
                logging.info(f"{str(self.ip)}: {e}")

        if not ignore_errors:
            # if it fails to validate, it is likely an error
            validation = self._validate_command_output(data)
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
        # get the token
        data = await self.send_command("get_token")

        # encrypt the admin password with the salt
        pwd = _crypt(self.admin_pwd, "$1$" + data["Msg"]["salt"] + "$")
        pwd = pwd.split("$")

        # take the 4th item from the pwd split
        host_passwd_md5 = pwd[3]

        # encrypt the pwd with the time and new salt
        tmp = _crypt(pwd[3] + data["Msg"]["time"], "$1$" + data["Msg"]["newsalt"] + "$")
        tmp = tmp.split("$")

        # take the 4th item from the encrypted pwd split
        host_sign = tmp[3]

        # set the current token
        self.current_token = {
            "host_sign": host_sign,
            "host_passwd_md5": host_passwd_md5,
        }
        return self.current_token

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
        # get the token and password from the miner
        token_data = await self.get_token()

        # parse pool data
        if not pool_1:
            raise APIError("No pools set.")
        elif pool_2 and pool_3:
            command = {
                "cmd": "update_pools",
                "pool1": pool_1,
                "worker1": worker_1,
                "passwd1": passwd_1,
                "pool2": pool_2,
                "worker2": worker_2,
                "passwd2": passwd_2,
                "pool3": pool_3,
                "worker3": worker_3,
                "passwd3": passwd_3,
            }
        elif pool_2:
            command = {
                "cmd": "update_pools",
                "pool1": pool_1,
                "worker1": worker_1,
                "passwd1": passwd_1,
                "pool2": pool_2,
                "worker2": worker_2,
                "passwd2": passwd_2,
            }
        else:
            command = {
                "cmd": "update_pools",
                "pool1": pool_1,
                "worker1": worker_1,
                "passwd1": passwd_1,
            }
        # encode the command with the token data
        enc_command = create_privileged_cmd(token_data, command)
        # send the command
        return await self.send_command(enc_command)

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
        command = {"cmd": "restart_btminer"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
            command = {"cmd": "power_off", "respbefore": "true"}
        else:
            command = {"cmd": "power_off", "respbefore": "false"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        command = {"cmd": "power_on"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        command = {"cmd": "set_led", "param": "auto"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_led(
        self,
        color: str = "red",
        period: int = 2000,
        duration: int = 1000,
        start: int = 0,
    ) -> dict:
        """Set the LED on the miner using the API.
        <details>
            <summary>Expand</summary>

        Set the LED on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            color: The LED color to set, either 'red' or 'green'.
            period: The flash cycle in ms.
            duration: LED on time in the cycle in ms.
            start: LED on time offset in the cycle in ms.
        Returns:

            A reply informing of the status of setting the LED.
        </details>
        """
        command = {
            "cmd": "set_led",
            "color": color,
            "period": period,
            "duration": duration,
            "start": start,
        }
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        command = {"cmd": "set_low_power"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def update_firmware(self):  # noqa - static
        """Not implemented."""
        # to be determined if this will be added later
        # requires a file stream in bytes
        return NotImplementedError

    async def reboot(self) -> dict:
        """Reboot the miner using the API.
        <details>
            <summary>Expand</summary>

        Returns:

            A reply informing of the status of the reboot.
        </details>
        """
        command = {"cmd": "reboot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def factory_reset(self) -> dict:
        """Reset the miner to factory defaults.
        <details>
            <summary>Expand</summary>

        Returns:

            A reply informing of the status of the reset.
        </details>
        """
        command = {"cmd": "factory_reset"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        # check if password length is greater than 8 bytes
        if len(new_pwd.encode("utf-8")) > 8:
            raise APIError(
                f"New password too long, the max length is 8.  "
                f"Password size: {len(new_pwd.encode('utf-8'))}"
            )
        command = {"cmd": "update_pwd", "old": old_pwd, "new": new_pwd}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        if not -10 < percent < 100:
            raise APIError(
                f"Frequency % is outside of the allowed "
                f"range.  Please set a % between -10 and "
                f"100"
            )
        command = {"cmd": "set_target_freq", "percent": str(percent)}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        command = {"cmd": "enable_btminer_fast_boot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        command = {"cmd": "disable_btminer_fast_boot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        command = {"cmd": "enable_web_pools"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        command = {"cmd": "disable_web_pools"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        command = {"cmd": "set_hostname", "hostname": hostname}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_power_pct(self, percent: int) -> dict:
        """Set the power percentage of the miner.

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
        command = {"cmd": "set_power_pct", "percent": str(percent)}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def pre_power_on(self, complete: bool, msg: str) -> dict:
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

        if not msg == "wait for adjust temp" or "adjust complete" or "adjust continue":
            raise APIError(
                "Message is incorrect, please choose one of "
                '["wait for adjust temp", '
                '"adjust complete", '
                '"adjust continue"]'
            )
        if complete:
            complete = "true"
        else:
            complete = "false"
        command = {"cmd": "pre_power_on", "complete": complete, "msg": msg}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

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
        return await self.send_command("get_miner_info")
