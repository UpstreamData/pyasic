import asyncio
import re
import json
import hashlib
import binascii
import base64
import logging

from passlib.handlers.md5_crypt import md5_crypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from API import BaseMinerAPI, APIError
from settings import WHATSMINER_PWD


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

    :param word: The word to be encrypted.
    :param salt: The salt to encrypt the word.
    :return: An MD5 hash of the word with the salt.
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

    :param string: The string to lengthen to a multiple of 16 and
    encode.

    :return: The input string as bytes with a multiple of 16 as the
    length.
    """
    while len(string) % 16 != 0:
        string += "\0"
    return str.encode(string)  # return bytes


def parse_btminer_priviledge_data(token_data: dict, data: dict):
    """Parses data returned from the BTMiner privileged API.

    Parses data from the BTMiner privileged API using the the token
    from the API in an AES format.

    :param token_data: The token information from self.get_token().
    :param data: The data to parse, returned from the API.

    :return: A decoded dict version of the privileged command output.
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

    :param token_data: The token information from self.get_token().
    :param command: The command to turn into a privileged command.

    :return: The encrypted privileged command to be sent to the miner.
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
    methods for sending commands to it.  The self.send_command()
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

    :param ip: The IP of the miner to reference the API on.
    :param port: The port to reference the API on.  Default is 4028.
    :param pwd: The admin password of the miner.  Default is admin.
    """

    def __init__(self, ip, port=4028, pwd: str = WHATSMINER_PWD):
        super().__init__(ip, port)
        self.admin_pwd = pwd
        self.current_token = None

    async def send_command(
        self,
        command: str or bytes,
        parameters: str or int or bool = None,
        ignore_errors: bool = False,
    ) -> dict:
        """Send a command to the miner API.

        Send a command using an asynchronous connection, load the data,
        parse encoded data if needed, and return the result.

        :param command: The command to send to the miner.
        :param parameters: Parameters to pass to the command.
        :param ignore_errors: Ignore the E (Error) status code from the
        API.

        :return: The data received from the API after sending the
        command.
        """
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

        data = self.load_api_data(data)

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
            validation = self.validate_command_output(data)
            if not validation[0]:
                raise APIError(validation[1])

        # return the parsed json as a dict
        return data

    async def get_token(self):
        """Gets token information from the API.

        :return: An encoded token and md5 password, which are used
        for the privileged API.
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
    ):
        """Update the pools of the miner using the API.

        Update the pools of the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        :param pool_1: The URL to update pool 1 to.
        :param worker_1: The worker name for pool 1 to update to.
        :param passwd_1: The password for pool 1 to update to.
        :param pool_2: The URL to update pool 2 to.
        :param worker_2: The worker name for pool 2 to update to.
        :param passwd_2: The password for pool 2 to update to.
        :param pool_3: The URL to update pool 3 to.
        :param worker_3: The worker name for pool 3 to update to.
        :param passwd_3: The password for pool 3 to update to.
        :return: A dict from the API to confirm the pools were updated.
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

    async def restart(self):
        """Restart BTMiner using the API.

        Restart BTMiner using the API, only works after changing
        the password of the miner using the Whatsminer tool.

        :return: A reply informing of the restart.
        """
        command = {"cmd": "restart_btminer"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def power_off(self, respbefore: bool = True):
        """Power off the miner using the API.

        Power off the miner using the API, only works after changing
        the password of the miner using the Whatsminer tool.

        :param respbefore: Whether to respond before powering off.
        :return: A reply informing of the status of powering off.
        """
        if respbefore:
            command = {"cmd": "power_off", "respbefore": "true"}
        else:
            command = {"cmd": "power_off", "respbefore": "false"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def power_on(self):
        """Power on the miner using the API.

        Power on the miner using the API, only works after changing
        the password of the miner using the Whatsminer tool.

        :return: A reply informing of the status of powering on.
        """
        command = {"cmd": "power_on"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def reset_led(self):
        """Reset the LED on the miner using the API.

        Reset the LED on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        :return: A reply informing of the status of resetting the LED.
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
    ):
        """Set the LED on the miner using the API.

        Set the LED on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        :param color: The LED color to set, either 'red' or 'green'.
        :param period: The flash cycle in ms.
        :param duration: LED on time in the cycle in ms.
        :param start: LED on time offset in the cycle in ms.
        :return: A reply informing of the status of setting the LED.
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

    async def set_low_power(self):
        """Set low power mode on the miner using the API.

        Set low power mode on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        :return: A reply informing of the status of setting low power
        mode.
        """
        command = {"cmd": "set_low_power"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def update_firmware(self):  # noqa - static
        # to be determined if this will be added later
        # requires a file stream in bytes
        return NotImplementedError

    async def reboot(self):
        """Reboot the miner using the API.

        :return: A reply informing of the status of the reboot.
        """
        command = {"cmd": "reboot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def factory_reset(self):
        """Reset the miner to factory defaults.

        :return: A reply informing of the status of the reset.
        """
        command = {"cmd": "factory_reset"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def update_pwd(self, old_pwd: str, new_pwd: str):
        """Update the admin user's password.

        Update the admin user's password, only works after changing the
        password of the miner using the Whatsminer tool.  New password
        has a max length of 8 bytes, using letters, numbers, and
        underscores.

        :param old_pwd: The old admin password.
        :param new_pwd: The new password to set.
        :return: A reply informing of the status of setting the
        password.
        """
        # check if password length is greater than 8 bytes
        if len(new_pwd.encode("utf-8")) > 8:
            return APIError(
                f"New password too long, the max length is 8.  "
                f"Password size: {len(new_pwd.encode('utf-8'))}"
            )
        command = {"cmd": "update_pwd", "old": old_pwd, "new": new_pwd}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_target_freq(self, percent: int):
        """Update the target frequency.

        Update the target frequency, only works after changing the
        password of the miner using the Whatsminer tool. The new
        frequency must be between -10% and 100%.

        :param percent: The frequency % to set.
        :return: A reply informing of the status of setting the
        frequency.
        """
        if not -10 < percent < 100:
            return APIError(
                f"Frequency % is outside of the allowed "
                f"range.  Please set a % between -10 and "
                f"100"
            )
        command = {"cmd": "set_target_freq", "percent": str(percent)}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def enable_fast_boot(self):
        """Turn on fast boot.

        Turn on fast boot, only works after changing the password of
        the miner using the Whatsminer tool.

        :return: A reply informing of the status of enabling fast boot.
        """
        command = {"cmd": "enable_btminer_fast_boot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def disable_fast_boot(self):
        """Turn off fast boot.

        Turn off fast boot, only works after changing the password of
        the miner using the Whatsminer tool.

        :return: A reply informing of the status of disabling fast boot.
        """
        command = {"cmd": "disable_btminer_fast_boot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def enable_web_pools(self):
        """Turn on web pool updates.

        Turn on web pool updates, only works after changing the
        password of the miner using the Whatsminer tool.

        :return: A reply informing of the status of enabling web pools.
        """
        command = {"cmd": "enable_web_pools"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def disable_web_pools(self):
        """Turn off web pool updates.

        Turn off web pool updates, only works after changing the
        password of the miner using the Whatsminer tool.

        :return: A reply informing of the status of disabling web
        pools.
        """
        command = {"cmd": "disable_web_pools"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_hostname(self, hostname: str):
        """Set the hostname of the miner.

        Set the hostname of the miner, only works after changing the
        password of the miner using the Whatsminer tool.


        :param hostname: The new hostname to use.
        :return: A reply informing of the status of setting the
        hostname.
        """
        command = {"cmd": "set_hostname", "hostname": hostname}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_power_pct(self, percent: int):
        """Set the power percentage of the miner.

        Set the power percentage of the miner, only works after changing
        the password of the miner using the Whatsminer tool.

        :param percent: The power percentage to set.
        :return: A reply informing of the status of setting the
        power percentage.
        """

        if not 0 < percent < 100:
            return APIError(
                f"Power PCT % is outside of the allowed "
                f"range.  Please set a % between 0 and "
                f"100"
            )
        command = {"cmd": "set_power_pct", "percent": str(percent)}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def pre_power_on(self, complete: bool, msg: str):
        """Configure or check status of pre power on.

        Configure or check status of pre power on, only works after
        changing the password of the miner using the Whatsminer tool.

        :param complete: check whether pre power on is complete.
        :param msg: the message to check.
        "wait for adjust temp" or
        "adjust complete" or
        "adjust continue"
        :return: A reply informing of the status of pre power on.
        """

        if not msg == "wait for adjust temp" or "adjust complete" or "adjust continue":
            return APIError(
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

    async def summary(self):
        """Get the summary status from the miner.

        :return: Summary status of the miner.
        """
        return await self.send_command("summary")

    async def pools(self):
        """Get the pool status from the miner.

        :return: Pool status of the miner.
        """
        return await self.send_command("pools")

    async def devs(self):
        """Get data on each PGA/ASC with their details.

        :return: Data on each PGA/ASC with their details.
        """
        return await self.send_command("devs")

    async def edevs(self):
        """Get data on each PGA/ASC with their details, ignoring
         blacklisted and zombie devices.

        :return: Data on each PGA/ASC with their details.
        """
        return await self.send_command("edevs")

    async def devdetails(self):
        """Get data on all devices with their static details.

        :return: Data on all devices with their static details.
        """
        return await self.send_command("devdetails")

    async def get_psu(self):
        """Get data on the PSU and power information.

        :return: Data on the PSU and power information.
        """
        return await self.send_command("get_psu")

    async def version(self):
        """Get version data for the miner.

        Get version data for the miner.  This calls another function,
        self.get_version(), but is named version to stay consistent
        with the other miner APIs.

        :return: Version data for the miner.
        """
        return await self.get_version()

    async def get_version(self):
        """Get version data for the miner.

        :return: Version data for the miner.
        """
        return await self.send_command("get_version")

    async def status(self):
        """Get BTMiner status and firmware version.

        :return: BTMiner status and firmware version.
        """
        return await self.send_command("status")

    async def get_miner_info(self):
        """Get general miner info.

        :return: General miner info.
        """
        return await self.send_command("get_miner_info")
