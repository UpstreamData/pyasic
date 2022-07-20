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

from typing import TypeVar, Tuple, List, Union
from collections.abc import AsyncIterable
from pyasic.miners import BaseMiner
import httpx

from pyasic.miners.antminer import *
from pyasic.miners.avalonminer import *
from pyasic.miners.whatsminer import *

from pyasic.miners._backends.cgminer import CGMiner  # noqa - Ignore _module import
from pyasic.miners._backends.bmminer import BMMiner  # noqa - Ignore _module import
from pyasic.miners._backends.bosminer import BOSMiner  # noqa - Ignore _module import
from pyasic.miners._backends.btminer import BTMiner  # noqa - Ignore _module import
from pyasic.miners._backends.bosminer_old import (  # noqa - Ignore _module import
    BOSMinerOld,
)

from pyasic.miners.unknown import UnknownMiner

from pyasic.API import APIError

import asyncio
import ipaddress
import json
import logging

from pyasic.settings import PyasicSettings

import asyncssh

AnyMiner = TypeVar("AnyMiner", bound=BaseMiner)

MINER_CLASSES = {
    "Antminer S9": {
        "Default": BOSMinerS9,
        "BOSMiner": BOSMinerOld,
        "BOSMiner+": BOSMinerS9,
        "BMMiner": BMMinerS9,
        "CGMiner": CGMinerS9,
    },
    "Antminer S9i": {
        "Default": BMMinerS9i,
        "BMMiner": BMMinerS9i,
    },
    "Antminer S17": {
        "Default": BMMinerS17,
        "BOSMiner+": BOSMinerS17,
        "BMMiner": BMMinerS17,
        "CGMiner": CGMinerS17,
    },
    "Antminer S17+": {
        "Default": BMMinerS17Plus,
        "BOSMiner+": BOSMinerS17Plus,
        "BMMiner": BMMinerS17Plus,
        "CGMiner": CGMinerS17Plus,
    },
    "Antminer S17 Pro": {
        "Default": BMMinerS17Pro,
        "BOSMiner+": BOSMinerS17Pro,
        "BMMiner": BMMinerS17Pro,
        "CGMiner": CGMinerS17Pro,
    },
    "Antminer S17e": {
        "Default": BMMinerS17e,
        "BOSMiner+": BOSMinerS17e,
        "BMMiner": BMMinerS17e,
        "CGMiner": CGMinerS17e,
    },
    "Antminer T17": {
        "Default": BMMinerT17,
        "BOSMiner+": BOSMinerT17,
        "BMMiner": BMMinerT17,
        "CGMiner": CGMinerT17,
    },
    "Antminer T17+": {
        "Default": BMMinerT17Plus,
        "BOSMiner+": BOSMinerT17Plus,
        "BMMiner": BMMinerT17Plus,
        "CGMiner": CGMinerT17Plus,
    },
    "Antminer T17e": {
        "Default": BMMinerT17e,
        "BOSMiner+": BOSMinerT17e,
        "BMMiner": BMMinerT17e,
        "CGMiner": CGMinerT17e,
    },
    "Antminer S19": {
        "Default": BMMinerS19,
        "BOSMiner+": BOSMinerS19,
        "BMMiner": BMMinerS19,
        "CGMiner": CGMinerS19,
    },
    "Antminer S19 Pro": {
        "Default": BMMinerS19Pro,
        "BOSMiner+": BOSMinerS19Pro,
        "BMMiner": BMMinerS19Pro,
        "CGMiner": CGMinerS19Pro,
    },
    "Antminer S19j": {
        "Default": BMMinerS19j,
        "BOSMiner+": BOSMinerS19j,
        "BMMiner": BMMinerS19j,
        "CGMiner": CGMinerS19j,
    },
    "Antminer S19j Pro": {
        "Default": BMMinerS19jPro,
        "BOSMiner+": BOSMinerS19jPro,
        "BMMiner": BMMinerS19jPro,
        "CGMiner": CGMinerS19jPro,
    },
    "Antminer S19a": {
        "Default": BMMinerS19a,
        "BMMiner": BMMinerS19a,
    },
    "Antminer T19": {
        "Default": BMMinerT19,
        "BOSMiner+": BOSMinerT19,
        "BMMiner": BMMinerT19,
        "CGMiner": CGMinerT19,
    },
    "M20S": {
        "Default": BTMinerM20S,
        "BTMiner": BTMinerM20S,
        "10": BTMinerM20SV10,
        "20": BTMinerM20SV20,
    },
    "M20S+": {
        "Default": BTMinerM20SPlus,
        "BTMiner": BTMinerM20SPlus,
    },
    "M21": {
        "Default": BTMinerM21,
        "BTMiner": BTMinerM21,
    },
    "M21S": {
        "Default": BTMinerM21S,
        "BTMiner": BTMinerM21S,
        "60": BTMinerM21SV60,
        "20": BTMinerM21SV20,
    },
    "M21S+": {
        "Default": BTMinerM21SPlus,
        "BTMiner": BTMinerM21SPlus,
    },
    "M30S": {
        "Default": BTMinerM30S,
        "BTMiner": BTMinerM30S,
        "50": BTMinerM30SV50,
        "G20": BTMinerM30SVG20,
        "E20": BTMinerM30SVE20,
        "E10": BTMinerM30SVE10,
    },
    "M30S+": {
        "Default": BTMinerM30SPlus,
        "BTMiner": BTMinerM30SPlus,
        "F20": BTMinerM30SPlusVF20,
        "E40": BTMinerM30SPlusVE40,
        "G60": BTMinerM30SPlusVG60,
    },
    "M30S++": {
        "Default": BTMinerM30SPlusPlus,
        "BTMiner": BTMinerM30SPlusPlus,
        "G40": BTMinerM30SPlusPlusVG40,
        "G30": BTMinerM30SPlusPlusVG30,
    },
    "M31S": {
        "Default": BTMinerM31S,
        "BTMiner": BTMinerM31S,
    },
    "M31S+": {
        "Default": BTMinerM31SPlus,
        "BTMiner": BTMinerM31SPlus,
        "E20": BTMinerM31SPlusVE20,
    },
    "M32S": {
        "Default": BTMinerM32S,
        "BTMiner": BTMinerM32S,
    },
    "AvalonMiner 721": {
        "Default": CGMinerAvalon721,
        "CGMiner": CGMinerAvalon721,
    },
    "AvalonMiner 741": {
        "Default": CGMinerAvalon741,
        "CGMiner": CGMinerAvalon741,
    },
    "AvalonMiner 761": {
        "Default": CGMinerAvalon761,
        "CGMiner": CGMinerAvalon761,
    },
    "AvalonMiner 821": {
        "Default": CGMinerAvalon821,
        "CGMiner": CGMinerAvalon821,
    },
    "AvalonMiner 841": {
        "Default": CGMinerAvalon841,
        "CGMiner": CGMinerAvalon841,
    },
    "AvalonMiner 851": {
        "Default": CGMinerAvalon851,
        "CGMiner": CGMinerAvalon851,
    },
    "AvalonMiner 921": {
        "Default": CGMinerAvalon921,
        "CGMiner": CGMinerAvalon921,
    },
    "AvalonMiner 1026": {
        "Default": CGMinerAvalon1026,
        "CGMiner": CGMinerAvalon1026,
    },
    "AvalonMiner 1047": {
        "Default": CGMinerAvalon1047,
        "CGMiner": CGMinerAvalon1047,
    },
    "AvalonMiner 1066": {
        "Default": CGMinerAvalon1066,
        "CGMiner": CGMinerAvalon1066,
    },
}


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MinerFactory(metaclass=Singleton):
    """A factory to handle identification and selection of the proper class of miner"""

    def __init__(self) -> None:
        self.miners = {}

    async def get_miner_generator(
        self, ips: List[Union[ipaddress.ip_address, str]]
    ) -> AsyncIterable[AnyMiner]:
        """
        Get Miner objects from ip addresses using an async generator.

        Returns an asynchronous generator containing Miners.

        Parameters:
            ips: a list of ip addresses to get miners for.

        Returns:
            An async iterable containing miners.
        """
        # get the event loop
        loop = asyncio.get_event_loop()
        # create a list of tasks
        scan_tasks = []
        # for each miner IP that was passed in, add a task to get its class
        for miner in ips:
            scan_tasks.append(loop.create_task(self.get_miner(miner)))
        # asynchronously run the tasks and return them as they complete
        scanned = asyncio.as_completed(scan_tasks)
        # loop through and yield the miners as they complete
        for miner in scanned:
            yield await miner

    async def get_miner(self, ip: Union[ipaddress.ip_address, str]) -> AnyMiner:
        """Decide a miner type using the IP address of the miner.

        Parameters:
            ip: An `ipaddress.ip_address` or string of the IP to find the miner.

        Returns:
            A miner class.
        """
        if isinstance(ip, str):
            ip = ipaddress.ip_address(ip)
        # check if the miner already exists in cache
        if ip in self.miners:
            return self.miners[ip]
        # if everything fails, the miner is already set to unknown
        miner = UnknownMiner(str(ip))
        api = None
        model = None
        ver = None

        # try to get the API multiple times based on retries
        for i in range(PyasicSettings().miner_factory_get_version_retries):
            try:
                # get the API type, should be BOSMiner, CGMiner, BMMiner, BTMiner, or None
                new_model, new_api, new_ver = await asyncio.wait_for(
                    self._get_miner_type(ip), timeout=10
                )
                # keep track of the API and model we found first
                if new_api and not api:
                    api = new_api
                if new_model and not model:
                    model = new_model
                if new_ver and not ver:
                    ver = new_ver
                # if we find the API and model, don't need to loop anymore
                if api and model:
                    break
            except asyncio.TimeoutError:
                logging.warning(f"{ip}: Get Miner Timed Out")
        # make sure we have model information
        if model:
            if not api:
                api = "Default"

            if model not in MINER_CLASSES.keys():
                if "avalon" in model:
                    if model == "avalon10":
                        miner = CGMinerAvalon1066(str(ip))
                    else:
                        miner = CGMinerAvalon821(str(ip))
                return miner
            if api not in MINER_CLASSES[model].keys():
                api = "Default"
            if ver in MINER_CLASSES[model].keys():
                miner = MINER_CLASSES[model][ver](str(ip))
                return miner
            miner = MINER_CLASSES[model][api](str(ip))

        # if we cant find a model, check if we found the API
        else:

            # return the miner base class with some API if we found it
            if api:
                if "BOSMiner+" in api:
                    miner = BOSMiner(str(ip))
                elif "BOSMiner" in api:
                    miner = BOSMinerOld(str(ip))
                elif "CGMiner" in api:
                    miner = CGMiner(str(ip))
                elif "BTMiner" in api:
                    miner = BTMiner(str(ip))
                elif "BMMiner" in api:
                    miner = BMMiner(str(ip))

        # save the miner to the cache at its IP if its not unknown
        if not isinstance(miner, UnknownMiner):
            self.miners[ip] = miner

        # return the miner
        return miner

    def clear_cached_miners(self) -> None:
        """Clear the miner factory cache."""
        # empty out self.miners
        self.miners = {}

    async def _get_miner_type(
        self, ip: Union[ipaddress.ip_address, str]
    ) -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
        data = None

        model = None
        api = None
        ver = None

        devdetails = None
        version = None
        try:
            # get device details and version data
            data = await self._send_api_command(str(ip), "devdetails+version")
            # validate success
            validation = await self._validate_command(data)
            if not validation[0]:
                raise APIError(validation[1])
            # copy each part of the main command to devdetails and version
            devdetails = data["devdetails"][0]
            version = data["version"][0]

        except APIError:
            try:
                # try devdetails and version separately (X19s mainly require this)
                # get devdetails and validate
                devdetails = await self._send_api_command(str(ip), "devdetails")
                validation = await self._validate_command(devdetails)
                if not validation[0]:
                    # if devdetails fails try version instead
                    devdetails = None

                    # get version and validate
                    version = await self._send_api_command(str(ip), "version")
                    validation = await self._validate_command(version)
                    if not validation[0]:
                        # finally try get_version (Whatsminers) and validate
                        version = await self._send_api_command(str(ip), "get_version")
                        validation = await self._validate_command(version)

                        # if this fails we raise an error to be caught below
                        if not validation[0]:
                            raise APIError(validation[1])
            except APIError as e:
                # catch APIError and let the factory know we cant get data
                logging.warning(f"{ip}: API Command Error: {e}")
                return None, None, None
        except OSError or ConnectionRefusedError:
            # miner refused connection on API port, we wont be able to get data this way
            # try ssh
            try:
                async with asyncssh.connect(
                    str(ip),
                    known_hosts=None,
                    username="root",
                    password="admin",
                    server_host_key_algs=["ssh-rsa"],
                ) as conn:
                    board_name = None
                    cmd = await conn.run("cat /tmp/sysinfo/board_name")
                    if cmd:
                        board_name = cmd.stdout.strip()

                if board_name:
                    if board_name == "am1-s9":
                        model = "Antminer S9"
                    if board_name == "am2-s17":
                        model = "Antminer S17"
                    api = "BOSMiner+"
                    return model, api, None

            except asyncssh.misc.PermissionDenied:
                try:
                    url = f"http://{self.ip}/cgi-bin/get_system_info.cgi"
                    auth = httpx.DigestAuth("root", "root")
                    async with httpx.AsyncClient() as client:
                        data = await client.get(url, auth=auth)
                    if data.status_code == 200:
                        data = data.json()
                    if "minertype" in data.keys():
                        model = data["minertype"]
                    if "bmminer" in "\t".join(data.keys()):
                        api = "BMMiner"
                except Exception as e:
                    logging.debug(f"Unable to get miner - {e}")
                    return None, None, None

        # if we have devdetails, we can get model data from there
        if devdetails:
            if "DEVDETAILS" in devdetails.keys() and not devdetails["DEVDETAILS"] == []:
                # check for model, for most miners
                if not devdetails["DEVDETAILS"][0]["Model"] == "":
                    # model of most miners
                    model = devdetails["DEVDETAILS"][0]["Model"]

                # if model fails, try driver
                else:
                    # some avalonminers have model in driver
                    model = devdetails["DEVDETAILS"][0]["Driver"]
            else:
                if "s9" in devdetails["STATUS"][0]["Description"]:
                    model = "Antminer S9"

        # if we have version we can get API type from here
        if version:
            if "VERSION" in version.keys():
                # check if there are any BMMiner strings in any of the dict keys
                if any("BMMiner" in string for string in version["VERSION"][0].keys()):
                    api = "BMMiner"

                # check if there are any CGMiner strings in any of the dict keys
                elif any(
                    "CGMiner" in string for string in version["VERSION"][0].keys()
                ):
                    api = "CGMiner"

                elif any(
                    "BTMiner" in string for string in version["VERSION"][0].keys()
                ):
                    api = "BTMiner"

                # check if there are any BOSMiner strings in any of the dict keys
                elif any(
                    "BOSminer" in string for string in version["VERSION"][0].keys()
                ):
                    api = "BOSMiner"
                    if version["VERSION"][0].get("BOSminer"):
                        if "plus" in version["VERSION"][0]["BOSminer"]:
                            api = "BOSMiner+"

                    if "BOSminer+" in version["VERSION"][0].keys():
                        api = "BOSMiner+"

                # check for avalonminers
                if version["VERSION"][0].get("PROD"):
                    _data = version["VERSION"][0]["PROD"].split("-")
                    model = _data[0]
                    if len(data) > 1:
                        ver = _data[1]
                elif version["VERSION"][0].get("MODEL"):
                    _data = version["VERSION"][0]["MODEL"].split("-")
                    model = f"AvalonMiner {_data[0]}"
                    if len(data) > 1:
                        ver = _data[1]

            # if all that fails, check the Description to see if it is a whatsminer
            if version.get("Description") and (
                "whatsminer" in version.get("Description")
            ):
                api = "BTMiner"

        # if we have no model from devdetails but have version, try to get it from there
        if version and not model:
            # make sure version isn't blank
            if (
                "VERSION" in version.keys()
                and version.get("VERSION")
                and not version.get("VERSION") == []
            ):
                # try to get "Type" which is model
                if version["VERSION"][0].get("Type"):
                    model = version["VERSION"][0]["Type"]

                # braiins OS bug check just in case
                elif "am2-s17" in version["STATUS"][0]["Description"]:
                    model = "Antminer S17"

        if model:
            # whatsminer have a V in their version string (M20SV41), remove everything after it
            if "V" in model:
                _ver = model.split("V")
                if len(_ver) > 1:
                    ver = model.split("V")[1]
                    model = model.split("V")[0]
            # don't need "Bitmain", just "Antminer XX" as model
            if "Bitmain " in model:
                model = model.replace("Bitmain ", "")
        return model, api, ver

    @staticmethod
    async def _validate_command(data: dict) -> Tuple[bool, Union[str, None]]:
        """Check if the returned command output is correctly formatted."""
        # check if the data returned is correct or an error
        if not data or data == {}:
            return False, "No API data."
        # if status isn't a key, it is a multicommand
        if "STATUS" not in data.keys():
            for key in data.keys():
                # make sure not to try to turn id into a dict
                if not key == "id":
                    # make sure they succeeded
                    if "STATUS" in data[key][0].keys():
                        if data[key][0]["STATUS"][0]["STATUS"] not in ["S", "I"]:
                            # this is an error
                            return False, f"{key}: " + data[key][0]["STATUS"][0]["Msg"]
        elif "id" not in data.keys():
            if data["STATUS"] not in ["S", "I"]:
                return False, data["Msg"]
        else:
            # make sure the command succeeded
            if data["STATUS"][0]["STATUS"] not in ("S", "I"):
                # this is an error
                if data["STATUS"][0]["STATUS"] not in ("S", "I"):
                    return False, data["STATUS"][0]["Msg"]
        return True, None

    @staticmethod
    async def _send_api_command(
        ip: Union[ipaddress.ip_address, str], command: str
    ) -> dict:
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(ip), 4028)
        except OSError as e:
            if e.errno in [10061, 22]:
                raise e
            logging.warning(f"{str(ip)} - Command {command}: {e}")
            return {}
        # create the command
        cmd = {"command": command}

        # send the command
        writer.write(json.dumps(cmd).encode("utf-8"))
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
            logging.debug(f"{str(ip)}: {e}")

        try:
            # some json from the API returns with a null byte (\x00) on the end
            if data.endswith(b"\x00"):
                # handle the null byte
                str_data = data.decode("utf-8")[:-1]
            else:
                # no null byte
                str_data = data.decode("utf-8")
            # fix an error with a btminer return having an extra comma that breaks json.loads()
            str_data = str_data.replace(",}", "}")
            # fix an error with a btminer return having a newline that breaks json.loads()
            str_data = str_data.replace("\n", "")
            # fix an error with a bmminer return missing a specific comma that breaks json.loads()
            str_data = str_data.replace("}{", "},{")
            # parse the json
            data = json.loads(str_data)
        # handle bad json
        except json.decoder.JSONDecodeError:
            # raise APIError(f"Decode Error: {data}")
            data = None

        # close the connection
        writer.close()
        await writer.wait_closed()

        return data
