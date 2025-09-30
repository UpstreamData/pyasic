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
import struct
import typing
import warnings
from collections.abc import AsyncGenerator
from enum import IntEnum
from typing import Annotated, Any, Literal

import httpx
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from passlib.handlers.md5_crypt import md5_crypt
from pydantic import BaseModel, ConfigDict, Field

from pyasic import settings
from pyasic.errors import APIError, APIWarning
from pyasic.misc import api_min_version, validate_command_output
from pyasic.rpc.base import BaseMinerRPCAPI

### IMPORTANT ###
# you need to change the password of the miners using the Whatsminer
# tool, then you can set them back to admin with this tool, but they
# must be changed to something else and set back to admin with this
# or the privileged API will not work using admin as the password.  If
# you change the password, you can pass that to this class as pwd,
# or add it as the Whatsminer_pwd in the settings.toml file.


class BTMinerAPICode(IntEnum):
    MSG_CMDOK = 0
    MSG_CMDERR = -1
    MSG_INVCMD = -2
    MSG_INVJSON = -3
    MSG_ACCDENY = -4
    MSG_OUT_OF_MEMORY = -5


class TokenResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    salt: str
    time: str
    newsalt: str


class TokenData(BaseModel):
    host_sign: str
    host_passwd_md5: str
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)


class BTMinerV3Command(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cmd: str
    param: Any | None = None


class BTMinerV3PrivilegedCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cmd: str
    param: Any | None = None
    ts: int
    account: str
    token: str


PrePowerOnMessage = (
    Literal["wait for adjust temp"]
    | Literal["adjust complete"]
    | Literal["adjust continue"]
)


class BTMinerV3Pool(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    url: str | None = None
    status: str | None = None
    account: str | None = None
    stratum_active: bool | None = Field(None, alias="stratum-active")
    reject_rate: float | None = Field(None, alias="reject-rate")
    last_share_time: float | None = Field(None, alias="last-share-time")


class BTMinerV3Summary(BaseModel):
    model_config = ConfigDict(extra="allow")

    elapsed: int
    bootup_time: int = Field(alias="bootup-time")
    freq_avg: float = Field(alias="freq-avg")
    target_freq: int | None = Field(None, alias="target-freq")
    factory_hash: float = Field(alias="factory-hash")
    hash_average: float = Field(alias="hash-average")
    hash_1min: float = Field(alias="hash-1min")
    hash_15min: float = Field(alias="hash-15min")
    hash_realtime: float = Field(alias="hash-realtime")
    power_rate: float = Field(alias="power-rate")
    power_5min: float = Field(alias="power-5min")
    power_realtime: float = Field(alias="power-realtime")
    environment_temperature: float = Field(alias="environment-temperature")
    board_temperature: list[float] = Field(alias="board-temperature")
    chip_temp_min: float = Field(alias="chip-temp-min")
    chip_temp_avg: float = Field(alias="chip-temp-avg")
    chip_temp_max: float = Field(alias="chip-temp-max")
    power_limit: int = Field(alias="power-limit")
    up_freq_finish: int = Field(alias="up-freq-finish")
    fan_speed_in: int = Field(alias="fan-speed-in")
    fan_speed_out: int = Field(alias="fan-speed-out")


class BTMinerV3EdevItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int
    slot: int
    hash_average: float = Field(alias="hash-average")
    factory_hash: float = Field(alias="factory-hash")
    freq: int
    effective_chips: int = Field(alias="effective-chips")
    chip_temp_min: float = Field(alias="chip-temp-min")
    chip_temp_avg: float = Field(alias="chip-temp-avg")
    chip_temp_max: float = Field(alias="chip-temp-max")


class BTMinerV3MinerStatusMsg(BaseModel):
    model_config = ConfigDict(extra="allow")

    pools: list[BTMinerV3Pool] = Field(default_factory=list)
    summary: BTMinerV3Summary | None = None
    edevs: list[BTMinerV3EdevItem] = Field(default_factory=list)


class BTMinerV3Network(BaseModel):
    model_config = ConfigDict(extra="allow")

    mac: str | None = None
    hostname: str | None = None


class BTMinerV3System(BaseModel):
    model_config = ConfigDict(extra="allow")

    api: str | None = None
    fwversion: str | None = None
    ledstatus: str | None = None


class BTMinerV3Hardware(BaseModel):
    model_config = ConfigDict(extra="allow")

    boards: int = 3


class BTMinerV3Power(BaseModel):
    model_config = ConfigDict(extra="allow")

    fanspeed: int | None = None


class BTMinerV3Miner(BaseModel):
    model_config = ConfigDict(extra="allow")

    power_limit_set: str | None = Field(None, alias="power-limit-set")
    pcbsn0: str | None = None
    pcbsn1: str | None = None
    pcbsn2: str | None = None


class BTMinerV3DeviceInfoMsg(BaseModel):
    model_config = ConfigDict(extra="allow")

    network: BTMinerV3Network = Field(default_factory=BTMinerV3Network)
    system: BTMinerV3System = Field(default_factory=BTMinerV3System)
    hardware: BTMinerV3Hardware = Field(default_factory=BTMinerV3Hardware)
    power: BTMinerV3Power = Field(default_factory=BTMinerV3Power)
    miner: BTMinerV3Miner = Field(default_factory=BTMinerV3Miner)


class BTMinerV3MinerStatusSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[BTMinerAPICode.MSG_CMDOK]
    when: int
    msg: BTMinerV3MinerStatusMsg
    desc: Literal["get.miner.status"]


class BTMinerV3DeviceInfoSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[BTMinerAPICode.MSG_CMDOK]
    when: int
    msg: BTMinerV3DeviceInfoMsg
    desc: Literal["get.device.info"]


class BTMinerV3SystemSettingMsg(BaseModel):
    model_config = ConfigDict(extra="allow")


class BTMinerV3SystemSettingSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[BTMinerAPICode.MSG_CMDOK]
    when: int
    msg: BTMinerV3SystemSettingMsg
    desc: Literal["get.system.setting"]


class BTMinerV3MinerHistoryMsg(BaseModel):
    model_config = ConfigDict(extra="allow")

    Data: str


class BTMinerV3MinerHistorySuccessResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[BTMinerAPICode.MSG_CMDOK]
    when: int
    msg: BTMinerV3MinerHistoryMsg
    desc: Literal["get.miner.history"]


class BTMinerV3MinerSettingMsg(BaseModel):
    model_config = ConfigDict(extra="allow")


class BTMinerV3MinerSettingSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[BTMinerAPICode.MSG_CMDOK]
    when: int
    msg: BTMinerV3MinerSettingMsg
    desc: Literal["get.miner.setting"]


class BTMinerV3LogDownloadMsg(BaseModel):
    model_config = ConfigDict(extra="allow")

    logsize: str


class BTMinerV3LogDownloadSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[BTMinerAPICode.MSG_CMDOK]
    when: int
    msg: BTMinerV3LogDownloadMsg
    desc: Literal["get.log.download"]


class BTMinerV3FanSettingMsg(BaseModel):
    model_config = ConfigDict(extra="allow")


class BTMinerV3FanSettingSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[BTMinerAPICode.MSG_CMDOK]
    when: int
    msg: BTMinerV3FanSettingMsg
    desc: Literal["get.fan.setting"]


class BTMinerV3SetCommandSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[BTMinerAPICode.MSG_CMDOK]
    when: int
    msg: Literal["ok"]
    desc: Literal[
        "set.system.reboot",
        "set.system.led",
        "set.miner.service",
        "set.miner.report",
        "set.miner.power_limit",
    ]


BTMinerV3SuccessResponse = Annotated[
    BTMinerV3MinerStatusSuccessResponse
    | BTMinerV3DeviceInfoSuccessResponse
    | BTMinerV3SystemSettingSuccessResponse
    | BTMinerV3MinerHistorySuccessResponse
    | BTMinerV3MinerSettingSuccessResponse
    | BTMinerV3LogDownloadSuccessResponse
    | BTMinerV3FanSettingSuccessResponse
    | BTMinerV3SetCommandSuccessResponse,
    Field(discriminator="desc"),
]


class BTMinerV3ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    code: Literal[
        BTMinerAPICode.MSG_CMDERR,
        BTMinerAPICode.MSG_INVCMD,
        BTMinerAPICode.MSG_INVJSON,
        BTMinerAPICode.MSG_ACCDENY,
        BTMinerAPICode.MSG_OUT_OF_MEMORY,
    ]
    when: int
    msg: str
    desc: str


BTMinerV3ResponseData = Annotated[
    BTMinerV3SuccessResponse | BTMinerV3ErrorResponse,
    Field(discriminator="code"),
]


class BTMinerV3Response(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: BTMinerV3ResponseData


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


def parse_btminer_priviledge_data(
    token_data: TokenData, data: dict[str, Any]
) -> dict[str, Any]:
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
    aeskey_hex = hashlib.sha256(token_data.host_passwd_md5.encode()).hexdigest()
    # unhexlify the aes key
    aeskey = binascii.unhexlify(aeskey_hex.encode())
    # create the required decryptor
    aes = Cipher(algorithms.AES(aeskey), modes.ECB())
    decryptor = aes.decryptor()
    # decode the message with the decryptor
    ret_msg: dict[str, Any] = json.loads(
        decryptor.update(base64.decodebytes(bytes(enc_data, encoding="utf8")))
        .rstrip(b"\0")
        .decode("utf8")
    )
    return ret_msg


def create_privileged_cmd(token_data: TokenData, command: dict[str, Any]) -> bytes:
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
    logging.debug("(Create Prilileged Command) - Creating Privileged Command")
    # add token to command
    command["token"] = token_data.host_sign
    # encode host_passwd data and get hexdigest
    aeskey_hex = hashlib.sha256(token_data.host_passwd_md5.encode()).hexdigest()
    # unhexlify the encoded host_passwd
    aeskey = binascii.unhexlify(aeskey_hex.encode())
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
        self.pwd: str = settings.get("default_whatsminer_rpc_password", "admin")
        self.token: TokenData | None = None

    async def multicommand(
        self, *commands: str, allow_warning: bool = True
    ) -> dict[str, Any]:
        """Creates and sends multiple commands as one command to the miner.

        Parameters:
            *commands: The commands to send as a multicommand to the miner.
            allow_warning: A boolean to supress APIWarnings.
        """
        # make sure we can actually run each command, otherwise they will fail
        commands_list = self._check_commands(*commands)
        # standard multicommand format is "command1+command2"
        # commands starting with "get_" and the "status" command aren't supported, but we can fake that

        split_commands = []

        for command in commands_list:
            if command.startswith("get_") or command == "status":
                commands_list.remove(command)
                # send seperately and append later
                split_commands.append(command)

        command = "+".join(commands_list)

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

        data: dict[str, Any] = {}
        for item in all_data:
            data.update(item)

        data["multicommand"] = True
        return data

    async def send_privileged_command(
        self,
        command: str,
        ignore_errors: bool = False,
        timeout: int = 10,
        **kwargs: Any,
    ) -> dict[str, Any]:
        try:
            return await self._send_privileged_command(
                command=command, ignore_errors=ignore_errors, timeout=timeout, **kwargs
            )
        except APIError as e:
            if not e.message == "can't access write cmd":
                raise
            # If we get here, we caught the specific error but didn't handle it
            raise
        # try:
        #     await self.open_api()
        # except Exception as e:
        #     raise APIError("Failed to open whatsminer API.") from e
        # return await self._send_privileged_command(
        #     command=command, ignore_errors=ignore_errors, timeout=timeout, **kwargs
        # )

    async def _send_privileged_command(
        self,
        command: str,
        ignore_errors: bool = False,
        timeout: int = 10,
        **kwargs: Any,
    ) -> dict[str, Any]:
        logging.debug(
            f"{self} - (Send Privileged Command) - {command} " + f"with args {kwargs}"
            if len(kwargs) > 0
            else ""
        )
        cmd = {"cmd": command, **kwargs}

        token_data = await self.get_token()
        enc_command = create_privileged_cmd(token_data, cmd)

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
        data_dict: dict[Any, Any] = self._load_api_data(data)

        try:
            data_dict = parse_btminer_priviledge_data(token_data, data_dict)
        except Exception as e:
            logging.info(f"{str(self.ip)}: {e}")

        if not ignore_errors:
            # if it fails to validate, it is likely an error
            validation = validate_command_output(data_dict)
            if not validation[0]:
                raise APIError(validation[1])

        # return the parsed json as a dict
        return data_dict

    async def get_token(self) -> TokenData:
        """Gets token information from the API.
        <details>
            <summary>Expand</summary>

        Returns:
            An encoded token and md5 password, which are used for the privileged API.
        </details>
        """
        logging.debug(f"{self} - (Get Token) - Getting token")
        if self.token:
            if self.token.timestamp > datetime.datetime.now() - datetime.timedelta(
                minutes=30
            ):
                return self.token

        # get the token
        data = await self.send_command("get_token")

        token_response = TokenResponse.model_validate(data["Msg"])

        # encrypt the admin password with the salt
        pwd_str = _crypt(self.pwd, "$1$" + token_response.salt + "$")
        pwd_parts = pwd_str.split("$")

        # take the 4th item from the pwd split
        host_passwd_md5 = pwd_parts[3]

        # encrypt the pwd with the time and new salt
        tmp_str = _crypt(
            pwd_parts[3] + token_response.time, "$1$" + token_response.newsalt + "$"
        )
        tmp_parts = tmp_str.split("$")

        # take the 4th item from the encrypted pwd split
        host_sign = tmp_parts[3]

        # set the current token
        self.token = TokenData(
            host_sign=host_sign,
            host_passwd_md5=host_passwd_md5,
            timestamp=datetime.datetime.now(),
        )
        logging.debug(f"{self} - (Get Token) - Gathered token data: {self.token}")
        return self.token

    async def open_api(self) -> bool:
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
        pool_2: str | None = None,
        worker_2: str | None = None,
        passwd_2: str | None = None,
        pool_3: str | None = None,
        worker_3: str | None = None,
        passwd_3: str | None = None,
    ) -> dict[str, Any]:
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

    async def restart(self) -> dict[str, Any]:
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

    async def power_off(self, respbefore: bool = True) -> dict[str, Any]:
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

    async def power_on(self) -> dict[str, Any]:
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

    async def reset_led(self) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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

    async def set_low_power(self) -> dict[str, Any]:
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

    async def set_high_power(self) -> dict[str, Any]:
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

    async def set_normal_power(self) -> dict[str, Any]:
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

    async def update_firmware(self, firmware: bytes) -> bool:
        """Upgrade the firmware running on the miner and using the firmware passed in bytes.
        <details>
            <summary>Expand</summary>

        Set the LED on the miner using the API, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            firmware (bytes): The firmware binary data to be uploaded.
        Returns:
            A boolean indicating the success of the firmware upgrade.
        Raises:
            APIError: If the miner is not ready for firmware update.
        </details>
        """
        ready = await self.send_privileged_command("upgrade_firmware")
        if not ready.get("Msg") == "ready":
            raise APIError(f"Not ready for firmware update: {self}")
        file_size = struct.pack("<I", len(firmware))
        await self._send_bytes(file_size + firmware)
        return True

    async def reboot(self, timeout: int = 10) -> dict[str, Any]:
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

    async def factory_reset(self) -> dict[str, Any]:
        """Reset the miner to factory defaults.
        <details>
            <summary>Expand</summary>

        Returns:
            A reply informing of the status of the reset.
        </details>
        """
        return await self.send_privileged_command("factory_reset")

    async def update_pwd(self, old_pwd: str, new_pwd: str) -> dict[str, Any]:
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
        ip: str | None = None,
        mask: str | None = None,
        gate: str | None = None,
        dns: str | None = None,
        host: str | None = None,
        dhcp: bool = True,
    ) -> dict[str, Any]:
        if dhcp:
            return await self.send_privileged_command("net_config", param="dhcp")
        if None in [ip, mask, gate, dns, host]:
            raise APIError("Incorrect parameters.")
        return await self.send_privileged_command(
            "net_config", ip=ip, mask=mask, gate=gate, dns=dns, host=host
        )

    async def set_target_freq(self, percent: int) -> dict[str, Any]:
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
                "Frequency % is outside of the allowed "
                "range.  Please set a % between -100 and "
                "100"
            )
        return await self.send_privileged_command(
            "set_target_freq", percent=str(percent)
        )

    async def enable_fast_boot(self) -> dict[str, Any]:
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

    async def disable_fast_boot(self) -> dict[str, Any]:
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

    async def enable_web_pools(self) -> dict[str, Any]:
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

    async def disable_web_pools(self) -> dict[str, Any]:
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

    async def set_hostname(self, hostname: str) -> dict[str, Any]:
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

    async def set_power_pct(self, percent: int) -> dict[str, Any]:
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
                "Power PCT % is outside of the allowed "
                "range.  Please set a % between 0 and "
                "100"
            )
        return await self.send_privileged_command("set_power_pct", percent=str(percent))

    async def pre_power_on(
        self, complete: bool, msg: PrePowerOnMessage
    ) -> dict[str, Any]:
        """Configure or check status of pre power on.

        <details>
            <summary>Expand</summary>

        Configure or check status of pre power on, only works after
        changing the password of the miner using the Whatsminer tool.

        Parameters:
            complete: check whether pre power on is complete.
            msg: the message to check.

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
    async def set_power_pct_v2(self, percent: int) -> dict[str, Any]:
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
                "Power PCT % is outside of the allowed "
                "range.  Please set a % between 0 and "
                "100"
            )
        return await self.send_privileged_command(
            "set_power_pct_v2", percent=str(percent)
        )

    @api_min_version("2.0.5")
    async def set_temp_offset(self, temp_offset: int) -> dict[str, Any]:
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
                "Temp offset is outside of the allowed "
                "range.  Please set a number between -30 and "
                "0."
            )

        return await self.send_privileged_command(
            "set_temp_offset", temp_offset=temp_offset
        )

    @api_min_version("2.0.5")
    async def adjust_power_limit(self, power_limit: int) -> dict[str, Any]:
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
    async def adjust_upfreq_speed(self, upfreq_speed: int) -> dict[str, Any]:
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
                "Upfreq speed is outside of the allowed "
                "range.  Please set a number between 0 (Normal) and "
                "9 (Fastest)."
            )
        return await self.send_privileged_command(
            "adjust_upfreq_speed", upfreq_speed=upfreq_speed
        )

    @api_min_version("2.0.5")
    async def set_poweroff_cool(self, poweroff_cool: bool) -> dict[str, Any]:
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
    async def set_fan_zero_speed(self, fan_zero_speed: bool) -> dict[str, Any]:
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

    async def summary(self) -> dict[str, Any]:
        """Get the summary status from the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            Summary status of the miner.
        </details>
        """
        return await self.send_command("summary")

    async def pools(self) -> dict[str, Any]:
        """Get the pool status from the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            Pool status of the miner.
        </details>
        """
        return await self.send_command("pools")

    async def devs(self) -> dict[str, Any]:
        """Get data on each PGA/ASC with their details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on each PGA/ASC with their details.
        </details>
        """
        return await self.send_command("devs")

    async def edevs(self) -> dict[str, Any]:
        """Get data on each PGA/ASC with their details, ignoring blacklisted and zombie devices.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on each PGA/ASC with their details.
        </details>
        """
        return await self.send_command("edevs")

    async def devdetails(self) -> dict[str, Any]:
        """Get data on all devices with their static details.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on all devices with their static details.
        </details>
        """
        return await self.send_command("devdetails")

    async def get_psu(self) -> dict[str, Any]:
        """Get data on the PSU and power information.
        <details>
            <summary>Expand</summary>

        Returns:
            Data on the PSU and power information.
        </details>
        """
        return await self.send_command("get_psu")

    async def version(self) -> dict[str, Any]:
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

    async def get_version(self) -> dict[str, Any]:
        """Get version data for the miner.
        <details>
            <summary>Expand</summary>

        Returns:
            Version data for the miner.
        </details>
        """
        return await self.send_command("get_version")

    async def status(self) -> dict[str, Any]:
        """Get BTMiner status and firmware version.
        <details>
            <summary>Expand</summary>

        Returns:
            BTMiner status and firmware version.
        </details>
        """
        return await self.send_command("status")

    async def get_miner_info(self) -> dict[str, Any]:
        """Get general miner info.
        <details>
            <summary>Expand</summary>

        Returns:
            General miner info.
        </details>
        """
        return await self.send_command("get_miner_info", allow_warning=False)

    @api_min_version("2.0.1")
    async def get_error_code(self) -> dict[str, Any]:
        """Get a list of error codes from the miner.

        <details>
            <summary>Expand</summary>
        Get a list of error codes from the miner.  Replaced `summary` as the location of error codes with API version 2.0.4.

        Returns:
            A list of error codes on the miner.
        </details>
        """
        return await self.send_command("get_error_code", allow_warning=False)


class BTMinerV3RPCAPI(BaseMinerRPCAPI):
    def __init__(self, ip: str, port: int = 4433, api_ver: str = "0.0.0") -> None:
        super().__init__(ip, port, api_ver=api_ver)

        self.salt: str | None = None
        self.pwd: str = "super"

    async def multicommand(
        self, *commands: str, allow_warning: bool = True
    ) -> dict[str, Any]:
        """Creates and sends multiple commands as one command to the miner.

        Parameters:
            *commands: The commands to send as a multicommand to the miner.
            allow_warning: A boolean to supress APIWarnings.

        """
        checked_commands = self._check_commands(*commands)
        result: dict[str, Any] = {"multicommand": True}

        for command in checked_commands:
            try:
                if ":" in command:
                    cmd, param = command.split(":", 1)
                else:
                    cmd, param = command, None

                response = await self.api_request(cmd, parameters=param)

                if response.desc == "get.device.info":
                    result[command] = [response.msg]
                elif response.desc == "get.miner.status":
                    if param == "summary":
                        result[command] = [response.msg.summary]
                    elif param == "edevs":
                        result[command] = [response.msg.edevs]
                    elif param == "pools":
                        result[command] = [response.msg.pools]
                    else:
                        result[command] = [response.msg]
                elif response.desc == "get.system.setting":
                    result[command] = [response.msg]
                elif response.desc == "get.miner.setting":
                    result[command] = [response.msg]
                elif response.desc == "get.fan.setting":
                    result[command] = [response.msg]
                else:
                    result[command] = [response.msg]
            except APIError:
                continue

        return result

    async def send_command(
        self,
        command: str,
        parameters: Any = None,
        ignore_errors: bool = False,
        allow_warning: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if ":" in command:
            parameters = command.split(":")[1]
            command = command.split(":")[0]

        cmd: BTMinerV3Command | BTMinerV3PrivilegedCommand

        if command.startswith("set."):
            salt = await self.get_salt()
            ts = int(datetime.datetime.now().timestamp())
            token_str = command + self.pwd + salt + str(ts)
            token_hashed = bytearray(
                base64.b64encode(hashlib.sha256(token_str.encode("utf-8")).digest())
            )
            b_arr = bytearray(token_hashed)
            b_arr[8] = 0
            str_token = b_arr.split(b"\x00")[0].decode("utf-8")

            cmd = BTMinerV3PrivilegedCommand(
                cmd=command, param=parameters, ts=ts, account="super", token=str_token
            )
        else:
            cmd = BTMinerV3Command(cmd=command, param=parameters)

        cmd_dict = cmd.model_dump()
        ser = json.dumps(cmd_dict).encode("utf-8")
        header = struct.pack("<I", len(ser))
        result: dict[str, Any] = json.loads(await self._send_bytes(header + ser))
        return result

    async def api_request(
        self,
        command: str,
        parameters: Any = None,
        **kwargs: Any,
    ) -> BTMinerV3SuccessResponse:
        data = await self.send_command(command, parameters=parameters, **kwargs)
        response = BTMinerV3Response.model_validate({"data": data})

        if response.data.code != BTMinerAPICode.MSG_CMDOK:
            logging.error(
                f"BTMiner API error: code={response.data.code.name}, msg={response.data.msg}"
            )
            raise APIError(
                f"BTMiner API error: {response.data.code.name} - {response.data.msg}"
            )
        return response.data

    async def _send_bytes(
        self,
        data: bytes,
        *,
        port: int | None = None,
        timeout: int = 100,
    ) -> bytes:
        if port is None:
            port = self.port
        logging.debug(f"{self} - ([Hidden] Send Bytes) - Sending")
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(self.ip), port)
        # handle OSError 121
        except OSError as e:
            if e.errno == 121:
                logging.warning(
                    f"{self} - ([Hidden] Send Bytes) - Semaphore timeout expired."
                )
            return b"{}"

        # send the command
        try:
            data_task = asyncio.create_task(self._read_bytes(reader, timeout=timeout))
            logging.debug(f"{self} - ([Hidden] Send Bytes) - Writing")
            writer.write(data)
            logging.debug(f"{self} - ([Hidden] Send Bytes) - Draining")
            await writer.drain()

            await data_task
            ret_data = data_task.result()
        except TimeoutError:
            logging.warning(f"{self} - ([Hidden] Send Bytes) - Read timeout expired.")
            return b"{}"

        # close the connection
        logging.debug(f"{self} - ([Hidden] Send Bytes) - Closing")
        writer.close()
        await writer.wait_closed()

        return ret_data

    def _check_commands(self, *commands: str) -> list[str]:
        return_commands = []

        for command in commands:
            if command.startswith("get.") or command.startswith("set."):
                return_commands.append(command)
            else:
                warnings.warn(
                    f"""Removing incorrect command: {command}
If you are sure you want to use this command please use API.send_command("{command}", ignore_errors=True) instead.""",
                    APIWarning,
                )
        return return_commands

    async def _read_bytes(self, reader: asyncio.StreamReader, timeout: int) -> bytes:
        ret_data = b""

        # loop to receive all the data
        logging.debug(f"{self} - ([Hidden] Send Bytes) - Receiving")
        try:
            header = await reader.readexactly(4)
            length = struct.unpack("<I", header)[0]
            ret_data = await reader.readexactly(length)
        except (asyncio.CancelledError, asyncio.TimeoutError) as e:
            raise e
        except Exception as e:
            logging.warning(f"{self} - ([Hidden] Send Bytes) - API Command Error {e}")
        return ret_data

    async def get_salt(self) -> str:
        if self.salt is not None:
            return self.salt
        data = await self.send_command("get.device.info", "salt")
        self.salt = data["msg"]["salt"]
        return self.salt

    @typing.no_type_check
    async def get_miner_report(self) -> AsyncGenerator[dict[str, Any], None]:
        if self.writer is None:
            await self.connect()

        result = asyncio.Queue()

        async def callback(data: dict[str, Any]) -> None:
            await result.put(data)

        cb_fn = callback

        try:
            self.cmd_callbacks["get.miner.report"].add(cb_fn)
            while True:
                yield await result.get()
                if self.writer.is_closing():
                    break
        finally:
            self.cmd_callbacks["get.miner.report"].remove(cb_fn)

    async def get_system_setting(self) -> BTMinerV3SystemSettingMsg:
        response = await self.api_request("get.system.setting")
        if not response.desc == "get.system.setting":
            raise APIError(f'Expected "get.system.setting" but got "{response.desc}"')
        return response.msg

    async def get_miner_status_summary(
        self,
    ) -> BTMinerV3Summary:
        response = await self.api_request("get.miner.status", parameters="summary")
        if not response.desc == "get.miner.status":
            raise APIError(f'Expected "get.miner.status" but got "{response.desc}"')
        if response.msg.summary is None:
            raise APIError("No summary data returned")
        return response.msg.summary

    async def get_miner_status_edevs(self) -> list[BTMinerV3EdevItem]:
        response = await self.api_request("get.miner.status", parameters="edevs")
        if not response.desc == "get.miner.status":
            raise APIError(f'Expected "get.miner.status" but got "{response.desc}"')
        return response.msg.edevs

    async def get_miner_status_pools(
        self,
    ) -> list[BTMinerV3Pool]:
        response = await self.api_request("get.miner.status", parameters="pools")
        if not response.desc == "get.miner.status":
            raise APIError(f'Expected "get.miner.status" but got "{response.desc}"')
        return response.msg.pools

    async def get_miner_history(self) -> dict[int, list[str]]:
        response = await self.api_request(
            "get.miner.history",
            parameters={
                "start": "1",
                "stop": str(datetime.datetime.now().timestamp()),
            },
        )
        if not response.desc == "get.miner.history":
            raise APIError(f'Expected "get.miner.history" but got "{response.desc}"')

        ret: dict[int, list[str]] = {}
        unparsed = response.msg.Data.strip()
        for item in unparsed.split(" "):
            list_item = item.split(",")
            timestamp = int(list_item.pop(0))
            ret[timestamp] = list_item
        return ret

    async def get_miner_setting(self) -> BTMinerV3MinerSettingMsg:
        response = await self.api_request("get.miner.setting")
        if not response.desc == "get.miner.setting":
            raise APIError(f'Expected "get.miner.setting" but got "{response.desc}"')
        return response.msg

    async def get_device_info(self) -> BTMinerV3DeviceInfoMsg:
        response = await self.api_request("get.device.info")
        if not response.desc == "get.device.info":
            raise APIError(f'Expected "get.device.info" but got "{response.desc}"')
        return response.msg

    async def get_log_download(self) -> BTMinerV3LogDownloadMsg:
        response = await self.api_request("get.log.download")
        if not response.desc == "get.log.download":
            raise APIError(f'Expected "get.log.download" but got "{response.desc}"')
        return response.msg

    async def get_fan_setting(self) -> BTMinerV3FanSettingMsg:
        response = await self.api_request("get.fan.setting")
        if not response.desc == "get.fan.setting":
            raise APIError(f'Expected "get.fan.setting" but got "{response.desc}"')
        return response.msg

    async def set_system_reboot(self) -> None:
        response = await self.api_request("set.system.reboot")
        if response.desc != "set.system.reboot":
            raise APIError(f'Expected "set.system.reboot" but got "{response.desc}"')

    async def set_system_factory_reset(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.system.factory_reset")

    async def set_system_update_firmware(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.system.update_firmware")

    async def set_system_net_config(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.system.net_config")

    async def set_system_led(self, leds: list[Any] | None = None) -> None:
        if leds is None:
            response = await self.api_request("set.system.led", parameters="auto")
        else:
            response = await self.api_request("set.system.led", parameters=leds)
        if response.desc != "set.system.led":
            raise APIError(f'Expected "set.system.led" but got "{response.desc}"')

    async def set_system_time_randomized(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.system.time_randomized")

    async def set_system_timezone(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.system.timezone")

    async def set_system_hostname(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.system.hostname")

    async def set_system_webpools(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.system.webpools")

    async def set_miner_target_freq(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.target_freq")

    async def set_miner_heat_mode(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.heat_mode")

    async def set_system_ntp_server(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.system.ntp_server")

    async def set_miner_service(self, value: str) -> None:
        response = await self.api_request("set.miner.service", parameters=value)
        if response.desc != "set.miner.service":
            raise APIError(f'Expected "set.miner.service" but got "{response.desc}"')

    async def set_miner_power_mode(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.power_mode")

    async def set_miner_cointype(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.cointype")

    async def set_miner_pools(self, *args: Any, **kwargs: Any) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.pools")

    async def set_miner_fastboot(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.fastboot")

    async def set_miner_power_percent(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.power_percent")

    async def set_miner_pre_power_on(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.pre_power_on")

    async def set_miner_restore_setting(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.restore_setting")

    async def set_miner_report(self, frequency: int = 1) -> None:
        response = await self.api_request(
            "set.miner.report", parameters={"gap": frequency}
        )
        if response.desc != "set.miner.report":
            raise APIError(f'Expected "set.miner.report" but got "{response.desc}"')

    async def set_miner_power_limit(self, power: int) -> None:
        response = await self.api_request("set.miner.power_limit", parameters=power)
        if response.desc != "set.miner.power_limit":
            raise APIError(
                f'Expected "set.miner.power_limit" but got "{response.desc}"'
            )

    async def set_miner_upfreq_speed(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.miner.upfreq_speed")

    async def set_log_upload(self, *args: Any, **kwargs: Any) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.log.upload")

    async def set_user_change_passwd(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.user.change_passwd")

    async def set_user_permission(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.user.permission")

    async def set_fan_temp_offset(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.fan.temp_offset")

    async def set_fan_poweroff_cool(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.fan.poweroff_cool")

    async def set_fan_zero_speed(
        self, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.fan.zero_speed")

    async def set_shell_debug(self, *args: Any, **kwargs: Any) -> dict[str, Any] | None:
        raise NotImplementedError
        return await self.send_command("set.shell.debug")
