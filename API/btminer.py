from API import BaseMinerAPI, APIError

from passlib.handlers.md5_crypt import md5_crypt
import asyncio
import re
import json
import hashlib
import binascii
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64


### IMPORTANT ###
# you need to change the password of the miners using
# the whatsminer tool, then you can set them back to
# admin with this tool, but they must be changed to
# something else and set back to admin with this or
# the privileged API will not work using admin as
# the password.


def _crypt(word: str, salt: str) -> str:
    # compile a standard format for the salt
    standard_salt = re.compile('\s*\$(\d+)\$([\w\./]*)\$')
    # check if the salt matches
    match = standard_salt.match(salt)
    # if the matching fails, the salt is incorrect
    if not match:
        raise ValueError("salt format is not correct")
    # save the matched salt in a new variable
    new_salt = match.group(2)
    # encrypt the word with the salt using md5
    result = md5_crypt.hash(word, salt=new_salt)
    return result


def _add_to_16(s: str) -> bytes:
    """Add null bytes to a string until the length is 16"""
    while len(s) % 16 != 0:
        s += '\0'
    return str.encode(s)  # return bytes


def parse_btminer_priviledge_data(token_data, data):
    # get the encoded data from the dict
    enc_data = data['enc']
    # get the aes key from the token data
    aeskey = hashlib.sha256(token_data['host_passwd_md5'].encode()).hexdigest()
    # unhexlify the aes key
    aeskey = binascii.unhexlify(aeskey.encode())
    # create the required decryptor
    aes = Cipher(algorithms.AES(aeskey), modes.ECB())
    decryptor = aes.decryptor()
    # decode the message with the decryptor
    ret_msg = json.loads(decryptor.update(
        base64.decodebytes(bytes(enc_data, encoding='utf8'))
    ).rstrip(b'\0').decode("utf8"))
    return ret_msg


def create_privileged_cmd(token_data: dict, command: dict) -> bytes:
    # add token to command
    command['token'] = token_data['host_sign']
    # encode host_passwd data and get hexdigest
    aeskey = hashlib.sha256(token_data['host_passwd_md5'].encode()).hexdigest()
    # unhexlify the encoded host_passwd
    aeskey = binascii.unhexlify(aeskey.encode())
    # create a new AES key
    aes = Cipher(algorithms.AES(aeskey), modes.ECB())
    encryptor = aes.encryptor()
    # dump the command to json
    api_json_str = json.dumps(command)
    # encode the json command with the aes key
    api_json_str_enc = base64.encodebytes(encryptor.update(_add_to_16(api_json_str))).decode("utf-8").replace("\n", "")
    # label the data as being encoded
    data_enc = {'enc': 1, 'data': api_json_str_enc}
    # dump the labeled data to json
    api_packet_str = json.dumps(data_enc)
    return api_packet_str.encode('utf-8')


class BTMinerAPI(BaseMinerAPI):
    def __init__(self, ip, port=4028, pwd: str = "admin"):
        super().__init__(ip, port)
        self.admin_pwd = pwd
        self.current_token = None

    async def send_command(self, command: str | bytes, **kwargs) -> dict:
        """Send an API command to the miner and return the result."""
        # check if command is a string, if its bytes its encoded and needs to be send raw
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
            print(e)

        data = self.load_api_data(data)

        # close the connection
        writer.close()
        await writer.wait_closed()

        # check if th returned data is encoded
        if 'enc' in data.keys():
            # try to parse the encoded data
            try:
                data = parse_btminer_priviledge_data(self.current_token, data)
            except Exception as e:
                print(e)

        # if it fails to validate, it is likely an error
        validation = self.validate_command_output(data)
        if not validation[0]:
            raise APIError(validation[1])

        # return the parsed json as a dict
        return data

    async def get_token(self):
        """
        API 'get_token' command.

        Returns an encoded token and md5 password, which are used for the privileged API.
        """
        data = await self.send_command("get_token")
        pwd = _crypt(self.admin_pwd, "$1$" + data["Msg"]["salt"] + '$')
        pwd = pwd.split('$')
        host_passwd_md5 = pwd[3]
        tmp = _crypt(pwd[3] + data["Msg"]["time"], "$1$" + data["Msg"]["newsalt"] + '$')
        tmp = tmp.split('$')
        host_sign = tmp[3]
        self.current_token = {'host_sign': host_sign, 'host_passwd_md5': host_passwd_md5}
        return {'host_sign': host_sign, 'host_passwd_md5': host_passwd_md5}

    #### PRIVILEGED COMMANDS ####
    # Please read the top of this file to learn
    # how to configure the whatsminer API to
    # use these commands.

    async def update_pools(self,
                           pool_1: str, worker_1: str, passwd_1: str,
                           pool_2: str = None, worker_2: str = None, passwd_2: str = None,
                           pool_3: str = None, worker_3: str = None, passwd_3: str = None):
        # get the token and password from the miner
        token_data = await self.get_token()

        # parse pool data
        if not pool_1:
            raise APIError("No pools set.")
        elif pool_2 and pool_3:
            command = {
                "cmd": "update_pools",
                "pool1": pool_1, "worker1": worker_1, "passwd1": passwd_1,
                "pool2": pool_2, "worker2": worker_2, "passwd2": passwd_2,
                "pool3": pool_3, "worker3": worker_3, "passwd3": passwd_3,
            }
        elif pool_2:
            command = {
                "cmd": "update_pools",
                "pool1": pool_1, "worker1": worker_1, "passwd1": passwd_1,
                "pool2": pool_2, "worker2": worker_2, "passwd2": passwd_2
            }
        else:
            command = {
                "cmd": "update_pools",
                "pool1": pool_1, "worker1": worker_1, "passwd1": passwd_1,
            }
        # encode the command with the token data
        enc_command = create_privileged_cmd(token_data, command)
        # send the command
        return await self.send_command(enc_command)

    async def restart(self):
        """
        API 'restart_btminer' command

        Returns a reply informing of the restart and restarts BTMiner.
        """
        command = {"cmd": "restart_btminer"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def power_off(self, respbefore: bool = True):
        """
        API 'power_off' command.

        Powers off the mining of the miner.

        Returns info on the power off.

        Parameters:
            respbefore (optional): respond before powering off.
        """
        if respbefore:
            command = {"cmd": "power_off", "respbefore": "true"}
        else:
            command = {"cmd": "power_off", "respbefore": "false"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def power_on(self):
        """
        API 'power_on' command.

        Powers on the mining of the miner.

        Returns info on the power on.
        """
        command = {"cmd": "power_on"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def reset_led(self):
        """
        API 'reset_led' command.

        Resets the LED flashing to normal.

        Returns a confirmation of resetting the LED.
        """
        command = {"cmd": "set_led", "param": "auto"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_led(self, color: str = "red", period: int = 2000, duration: int = 1000, start: int = 0):
        """
        API 'set_led' command.

        Sets the LED to do some pattern set with parameters.

        Returns a confirmation of setting the LED.
        
        Parameters:
            color: 'red' or 'green'
            period: flash cycle in ms
            duration: led on time in the cycle in ms
            start: led on time offset in the cycle in ms
        """
        command = {"cmd": "set_led", "color": color, "period": period, "duration": duration, "start": start}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_low_power(self):
        """
        API 'set_low_power' command.
        
        Sets the miner to low power mode.
        
        Returns the status of setting the miner to low power mode.
        """
        command = {"cmd": "set_low_power"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def update_firmware(self):
        # to be determined if this will be added later
        # requires a file stream in bytes
        return NotImplementedError

    async def reboot(self):
        """
        API 'reboot' command.
        
        Reboots the miner.
        
        Returns the status of the command then reboots.        
        """
        command = {"cmd": "reboot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def factory_reset(self):
        """
        API 'factory_reset' command.

        Resets the miner to factory defaults.

        Returns the status of the command then resets.        
        """
        command = {"cmd": "factory_reset"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def update_pwd(self, old_pwd: str, new_pwd: str):
        """
        API 'update_pwd' command.

        Updates the admin user's password.
        
        Returns the status of setting the password to the new password.
        
        Parameters:
              old_pwd: the old admin password.
              new_pwd: the new password to set. Max length of 8 bytes, using letters, numbers, and underscores.   
        """
        # check if password length is greater than 8 bytes
        if len(new_pwd.encode('utf-8')) > 8:
            return APIError(
                f"New password too long, the max length is 8.  Password size: {len(new_pwd.encode('utf-8'))}")
        command = {"cmd": "update_pwd", "old": old_pwd, "new": new_pwd}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_target_freq(self, percent: int):
        """
        API 'set_target_freq' command.

        Sets the frequency for the miner ot use.

        Returns the status of setting the frequency.       
        """
        if not -10 < percent < 100:
            return APIError(f"Frequency % is outside of the allowed range.  Please set a % between -10 and 100")
        command = {"cmd": "set_target_freq", "percent": str(percent)}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def enable_fast_boot(self):
        """
        API 'enable_fast_boot' command.

        Turns on the fast boot feature on the miner.

        Returns the status of setting the fast boot to on.        
        """
        command = {"cmd": "enable_btminer_fast_boot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def disable_fast_boot(self):
        """
        API 'disable'_fast_boot' command.

        Turns off the fast boot feature on the miner.

        Returns the status of setting the fast boot to off.        
        """
        command = {"cmd": "disable_btminer_fast_boot"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def enable_web_pools(self):
        """
        API 'enable_web_pools' command.

        Turns on the ability to change the pools through the web interface.

        Returns the status of setting the web pools to enabled.        
        """
        command = {"cmd": "enable_web_pools"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def disable_web_pools(self):
        """
        API 'disable_web_pools' command.

        Turns off the ability to change the pools through the web interface.

        Returns the status of setting the web pools to disabled.        
        """
        command = {"cmd": "disable_web_pools"}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_hostname(self, hostname: str):
        """
        API 'set_hostname' command.

        Sets the hostname of the miner.

        Returns the status of setting the hostname.        
        """
        command = {"cmd": "set_hostname", "hostname": hostname}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def set_power_pct(self, percent: int):
        """
        API 'set_power_pct' command.

        Sets the percent of power the miner should use.

        Returns the status of setting the power usage to this percent.

        Parameters:
            percent: the percent to set the power usage to, between 0 and 100.
        """

        if not 0 < percent < 100:
            return APIError(f"Power PCT % is outside of the allowed range.  Please set a % between 0 and 100")
        command = {"cmd": "set_power_pct", "percent": str(percent)}
        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, command)
        return await self.send_command(enc_command)

    async def pre_power_on(self, complete: bool, msg: str):
        """
        API 'pre_power_on' command.

        Preheats the miner for the 'power_on' command. Can also be used to query the status of pre powering on.

        Returns status of pre powering on.

        Parameters:
              complete: check whether or not it is complete.
              msg: the message to check. "wait for adjust temp" or "adjust complete" or "adjust continue"
        """

        if not msg == "wait for adjust temp" or "adjust complete" or "adjust continue":
            return APIError(
                'Message is incorrect, please choose one of '
                '["wait for adjust temp", "adjust complete", "adjust continue"]'
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
        """
        API 'summary' command.

        Returns a dict containing the status summary of the miner.
        """
        return await self.send_command("summary")

    async def pools(self):
        """
        API 'pools' command.

        Returns a dict containing the status of each pool.
        """
        return await self.send_command("pools")

    async def devs(self):
        """
        API 'devs' command.

        Returns a dict containing each PGA/ASC with their details.
        """
        return await self.send_command("devs")

    async def edevs(self):
        """
        API 'edevs' command.

        Returns a dict containing each PGA/ASC with their details,
        ignoring blacklisted devices and zombie devices.
        """
        return await self.send_command("edevs")

    async def devdetails(self):
        """
        API 'devdetails' command.

        Returns a dict containing all devices with their static details.
        """
        return await self.send_command("devdetails")

    async def get_psu(self):
        """
        API 'get_psu' command.

        Returns a dict containing PSU and power information.
        """
        return await self.send_command("get_psu")

    async def version(self):
        """
        API 'get_version' command.

        Returns a dict containing version information.
        """
        return await self.send_command("get_version")

    async def status(self):
        """
        API 'status' command.

        Returns a dict containing BTMiner status and firmware version.
        """
        return await self.send_command("status")

    async def get_miner_info(self):
        """
        API 'get_miner_info' command.

        Returns a dict containing general miner info.
        """
        return await self.send_command("get_miner_info")
