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
import ipaddress
import json
import logging
from collections.abc import AsyncIterable
from typing import List, Tuple, Union

import asyncssh
import httpx

from pyasic.errors import APIError
from pyasic.miners._backends.bmminer import BMMiner  # noqa - Ignore _module import
from pyasic.miners._backends.bosminer import BOSMiner  # noqa - Ignore _module import
from pyasic.miners._backends.bosminer_old import (  # noqa - Ignore _module import
    BOSMinerOld,
)
from pyasic.miners._backends.btminer import BTMiner  # noqa - Ignore _module import
from pyasic.miners._backends.cgminer import CGMiner  # noqa - Ignore _module import
from pyasic.miners.antminer import *
from pyasic.miners.avalonminer import *
from pyasic.miners.base import AnyMiner
from pyasic.miners.innosilicon import *
from pyasic.miners.unknown import UnknownMiner
from pyasic.miners.whatsminer import *
from pyasic.misc import Singleton
from pyasic.settings import PyasicSettings

MINER_CLASSES = {
    "ANTMINER S9": {
        "Default": BOSMinerS9,
        "BOSMiner": BOSMinerOld,
        "BOSMiner+": BOSMinerS9,
        "BMMiner": BMMinerS9,
        "CGMiner": CGMinerS9,
    },
    "ANTMINER S9I": {
        "Default": BMMinerS9i,
        "BMMiner": BMMinerS9i,
    },
    "ANTMINER T9": {
        "Default": BMMinerT9,
        "BMMiner": BMMinerT9,
        "Hiveon": HiveonT9,
        "CGMiner": CGMinerT9,
    },
    "ANTMINER S17": {
        "Default": BMMinerS17,
        "BOSMiner+": BOSMinerS17,
        "BMMiner": BMMinerS17,
        "CGMiner": CGMinerS17,
    },
    "ANTMINER S17+": {
        "Default": BMMinerS17Plus,
        "BOSMiner+": BOSMinerS17Plus,
        "BMMiner": BMMinerS17Plus,
        "CGMiner": CGMinerS17Plus,
    },
    "ANTMINER S17 PRO": {
        "Default": BMMinerS17Pro,
        "BOSMiner+": BOSMinerS17Pro,
        "BMMiner": BMMinerS17Pro,
        "CGMiner": CGMinerS17Pro,
    },
    "ANTMINER S17E": {
        "Default": BMMinerS17e,
        "BOSMiner+": BOSMinerS17e,
        "BMMiner": BMMinerS17e,
        "CGMiner": CGMinerS17e,
    },
    "ANTMINER T17": {
        "Default": BMMinerT17,
        "BOSMiner+": BOSMinerT17,
        "BMMiner": BMMinerT17,
        "CGMiner": CGMinerT17,
    },
    "ANTMINER T17+": {
        "Default": BMMinerT17Plus,
        "BOSMiner+": BOSMinerT17Plus,
        "BMMiner": BMMinerT17Plus,
        "CGMiner": CGMinerT17Plus,
    },
    "ANTMINER T17E": {
        "Default": BMMinerT17e,
        "BOSMiner+": BOSMinerT17e,
        "BMMiner": BMMinerT17e,
        "CGMiner": CGMinerT17e,
    },
    "ANTMINER S19": {
        "Default": BMMinerS19,
        "BOSMiner+": BOSMinerS19,
        "BMMiner": BMMinerS19,
        "CGMiner": CGMinerS19,
    },
    "ANTMINER S19 PRO": {
        "Default": BMMinerS19Pro,
        "BOSMiner+": BOSMinerS19Pro,
        "BMMiner": BMMinerS19Pro,
        "CGMiner": CGMinerS19Pro,
    },
    "ANTMINER S19J": {
        "Default": BMMinerS19j,
        "BOSMiner+": BOSMinerS19j,
        "BMMiner": BMMinerS19j,
        "CGMiner": CGMinerS19j,
    },
    "ANTMINER S19J PRO": {
        "Default": BMMinerS19jPro,
        "BOSMiner+": BOSMinerS19jPro,
        "BMMiner": BMMinerS19jPro,
        "CGMiner": CGMinerS19jPro,
    },
    "ANTMINER S19 XP": {
        "Default": BMMinerS19XP,
        "BMMiner": BMMinerS19XP,
    },
    "ANTMINER S19A": {
        "Default": BMMinerS19a,
        "BMMiner": BMMinerS19a,
    },
    "ANTMINER S19A PRO": {
        "Default": BMMinerS19aPro,
        "BMMiner": BMMinerS19aPro,
    },
    "ANTMINER T19": {
        "Default": BMMinerT19,
        "BOSMiner+": BOSMinerT19,
        "BMMiner": BMMinerT19,
        "CGMiner": CGMinerT19,
    },
    "M20": {
        "Default": BTMinerM20,
        "BTMiner": BTMinerM20,
        "10": BTMinerM20V10,
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
        "H60": BTMinerM30SPlusPlusVH60,
    },
    "M31S": {
        "Default": BTMinerM31S,
        "BTMiner": BTMinerM31S,
        "V10": BTMinerM31SV10,
        "V60": BTMinerM31SV60,
        "V70": BTMinerM31SV70,
    },
    "M31S+": {
        "Default": BTMinerM31SPlus,
        "BTMiner": BTMinerM31SPlus,
        "E20": BTMinerM31SPlusVE20,
        "30": BTMinerM31SPlusV30,
        "40": BTMinerM31SPlusV40,
        "60": BTMinerM31SPlusV60,
        "80": BTMinerM31SPlusV80,
        "90": BTMinerM31SPlusV90,
    },
    "M32S": {
        "Default": BTMinerM32S,
        "BTMiner": BTMinerM32S,
    },
    "M32": {
        "Default": BTMinerM32,
        "BTMiner": BTMinerM32,
        "20": BTMinerM32V20,
    },
    "M34S+": {
        "Default": BTMinerM34SPlus,
        "BTMiner": BTMinerM34SPlus,
        "E10": BTMinerM34SPlusVE10,
    },
    "M50": {
        "Default": BTMinerM50,
        "BTMiner": BTMinerM50,
        "H50": BTMinerM50VH50,
    },
    "AVALONMINER 721": {
        "Default": CGMinerAvalon721,
        "CGMiner": CGMinerAvalon721,
    },
    "AVALONMINER 741": {
        "Default": CGMinerAvalon741,
        "CGMiner": CGMinerAvalon741,
    },
    "AVALONMINER 761": {
        "Default": CGMinerAvalon761,
        "CGMiner": CGMinerAvalon761,
    },
    "AVALONMINER 821": {
        "Default": CGMinerAvalon821,
        "CGMiner": CGMinerAvalon821,
    },
    "AVALONMINER 841": {
        "Default": CGMinerAvalon841,
        "CGMiner": CGMinerAvalon841,
    },
    "AVALONMINER 851": {
        "Default": CGMinerAvalon851,
        "CGMiner": CGMinerAvalon851,
    },
    "AVALONMINER 921": {
        "Default": CGMinerAvalon921,
        "CGMiner": CGMinerAvalon921,
    },
    "AVALONMINER 1026": {
        "Default": CGMinerAvalon1026,
        "CGMiner": CGMinerAvalon1026,
    },
    "AVALONMINER 1047": {
        "Default": CGMinerAvalon1047,
        "CGMiner": CGMinerAvalon1047,
    },
    "AVALONMINER 1066": {
        "Default": CGMinerAvalon1066,
        "CGMiner": CGMinerAvalon1066,
    },
    "T3H+": {
        "Default": CGMinerInnosiliconT3HPlus,
        "CGMiner": CGMinerInnosiliconT3HPlus,
    },
    "Unknown": {"Default": UnknownMiner},
}


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
        model, api, ver = None, None, None

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
        miner = self._select_miner_from_classes(ip, model, api, ver)

        # save the miner to the cache at its IP if its not unknown
        if not isinstance(miner, UnknownMiner):
            self.miners[ip] = miner

        # return the miner
        return miner

    @staticmethod
    def _select_miner_from_classes(
        ip: ipaddress.ip_address,
        model: Union[str, None],
        api: Union[str, None],
        ver: Union[str, None],
    ) -> AnyMiner:
        miner = UnknownMiner(str(ip))
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

        return miner

    def clear_cached_miners(self) -> None:
        """Clear the miner factory cache."""
        # empty out self.miners
        self.miners = {}

    async def _get_miner_type(
        self, ip: Union[ipaddress.ip_address, str]
    ) -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
        model, api, ver = None, None, None

        try:
            devdetails, version = await self.__get_devdetails_and_version(ip)
        except APIError as e:
            # catch APIError and let the factory know we cant get data
            logging.warning(f"{ip}: API Command Error: {e}")
            return None, None, None
        except OSError or ConnectionRefusedError:
            # miner refused connection on API port, we wont be able to get data this way
            # try ssh
            try:
                _model = await self.__get_model_from_graphql(ip)
                if not _model:
                    _model = await self.__get_model_from_ssh(ip)
                if _model:
                    model = _model
                    api = "BOSMiner+"
            except asyncssh.misc.PermissionDenied:
                try:
                    data = await self.__get_system_info_from_web(ip)
                    if not data.get("success"):
                        _model = await self.__get_dragonmint_version_from_web(ip)
                        if _model:
                            model = _model
                    if "minertype" in data:
                        model = data["minertype"].upper()
                    if "bmminer" in "\t".join(data):
                        api = "BMMiner"
                except Exception as e:
                    logging.debug(f"Unable to get miner - {e}")
            return model, api, ver

        # if we have devdetails, we can get model data from there
        if devdetails:
            for _devdetails_key in ["Model", "Driver"]:
                try:
                    model = devdetails["DEVDETAILS"][0][_devdetails_key].upper()
                    if not model == "BITMICRO":
                        break
                except KeyError:
                    continue
            try:
                if devdetails[0]["STATUS"][0]["Msg"]:
                    model = await self.__get_model_from_graphql(ip)
                    if model:
                        api = "BOSMiner+"
            except (KeyError, TypeError, ValueError, IndexError):
                pass
            try:
                if not model:
                    # braiins OS bug check just in case
                    if "s9" in devdetails["STATUS"][0]["Description"]:
                        model = "ANTMINER S9"
                    if "s17" in version["STATUS"][0]["Description"]:
                        model = "ANTMINER S17"
            except (KeyError, TypeError, ValueError, IndexError):
                pass
            try:
                if not api:
                    if "boser" in version["STATUS"][0]["Description"]:
                        api = "BOSMiner+"
            except (KeyError, TypeError, ValueError, IndexError):
                pass
        else:
            try:
                _model = await self.__get_model_from_graphql(ip)
                if _model:
                    model = _model
                    api = "BOSMiner+"
            except (KeyError, TypeError, ValueError, IndexError):
                pass

        # if we have version we can get API type from here
        if version:
            try:
                if version[0]["STATUS"][0]["Msg"]:
                    model = await self.__get_model_from_graphql(ip)
                    if model:
                        api = "BOSMiner+"
                        return model, api, ver
            except (KeyError, TypeError, ValueError, IndexError):
                pass
            if "VERSION" in version:
                api_types = ["BMMiner", "CGMiner", "BTMiner"]
                # check basic API types, BOSMiner needs a special check
                for api_type in api_types:
                    if any(api_type in string for string in version["VERSION"][0]):
                        api = api_type

                # check if there are any BOSMiner strings in any of the dict keys
                if any("BOSminer" in string for string in version["VERSION"][0]):
                    api = "BOSMiner"
                    if version["VERSION"][0].get("BOSminer"):
                        if "plus" in version["VERSION"][0]["BOSminer"]:
                            api = "BOSMiner+"
                    if "BOSminer+" in version["VERSION"][0]:
                        api = "BOSMiner+"
                if any("BOSer" in string for string in version["VERSION"][0]):
                    api = "BOSMiner+"

                # check for avalonminers
                for _version_key in ["PROD", "MODEL"]:
                    try:
                        _data = version["VERSION"][0][_version_key].split("-")
                    except KeyError:
                        continue

                    model = _data[0].upper()
                    if _version_key == "MODEL":
                        model = f"AVALONMINER {_data[0]}"
                    if len(_data) > 1:
                        ver = _data[1]

            if version.get("Description") and (
                "whatsminer" in version.get("Description")
            ):
                api = "BTMiner"

        # if we have no model from devdetails but have version, try to get it from there
        if version and not model:
            try:
                model = version["VERSION"][0]["Type"].upper()
            except KeyError:
                pass

        if not model:
            stats = await self._send_api_command(str(ip), "stats")
            if stats:
                try:
                    _model = stats["STATS"][0]["Type"].upper()
                except KeyError:
                    pass
                else:
                    for split_point in [" BB", " XILINX", " (VNISH"]:
                        if split_point in _model:
                            _model = _model.split(split_point)[0]
                    if "PRO" in _model and " PRO" not in _model:
                        _model = _model.replace("PRO", " PRO")
                    model = _model
            else:
                _model = await self.__get_dragonmint_version_from_web(ip)
                if _model:
                    model = _model

        if model:
            if "DRAGONMINT" in model:
                _model = await self.__get_dragonmint_version_from_web(ip)
                if _model:
                    model = _model
            if " HIVEON" in model:
                # do hiveon check before whatsminer as HIVEON contains a V
                model = model.split(" HIVEON")[0]
                api = "Hiveon"
            # whatsminer have a V in their version string (M20SV41), everything after it is ver
            if "V" in model:
                _ver = model.split("V")
                if len(_ver) > 1:
                    ver = model.split("V")[1]
                    model = model.split("V")[0]
            # don't need "Bitmain", just "ANTMINER XX" as model
            if "BITMAIN " in model:
                model = model.replace("BITMAIN ", "")
        return model, api, ver

    async def __get_devdetails_and_version(
        self, ip
    ) -> Tuple[Union[dict, None], Union[dict, None]]:
        version = None
        try:
            # get device details and version data
            data = await self._send_api_command(str(ip), "devdetails+version")
            # validate success
            validation = await self._validate_command(data)
            if not validation[0]:
                try:
                    if data["version"][0]["STATUS"][0]["Msg"] == "Disconnected":
                        return data["devdetails"], data["version"]
                except (KeyError, TypeError):
                    pass
                raise APIError(validation[1])
            # copy each part of the main command to devdetails and version
            devdetails = data["devdetails"][0]
            version = data["version"][0]
            return devdetails, version
        except APIError:
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
        return devdetails, version

    @staticmethod
    async def __get_model_from_ssh(ip: ipaddress.ip_address) -> Union[str, None]:
        model = None
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
        if board_name == "am1-s9":
            model = "ANTMINER S9"
        if board_name == "am2-s17":
            model = "ANTMINER S17"
        return model

    @staticmethod
    async def __get_model_from_graphql(ip: ipaddress.ip_address) -> Union[str, None]:
        model = None
        url = f"http://{ip}/graphql"
        async with httpx.AsyncClient() as client:
            d = await client.post(url, json={"query": "{bosminer {info{modelName}}}"})
        if d.status_code == 200:
            model = (d.json()["data"]["bosminer"]["info"]["modelName"]).upper()
        return model

    @staticmethod
    async def __get_system_info_from_web(ip) -> dict:
        url = f"http://{ip}/cgi-bin/get_system_info.cgi"
        auth = httpx.DigestAuth("root", "root")
        async with httpx.AsyncClient() as client:
            data = await client.get(url, auth=auth)
        if data.status_code == 200:
            data = data.json()
        return data

    @staticmethod
    async def __get_dragonmint_version_from_web(
        ip: ipaddress.ip_address,
    ) -> Union[str, None]:
        response = None
        async with httpx.AsyncClient() as client:
            try:
                auth = (
                    await client.post(
                        f"http://{ip}/api/auth",
                        data={"username": "admin", "password": "admin"},
                    )
                ).json()["jwt"]
                response = (
                    await client.post(
                        f"http://{ip}/api/type",
                        headers={"Authorization": "Bearer " + auth},
                        data={},
                    )
                ).json()
            except Exception as e:
                logging.info(e)
        if response:
            return response["type"]

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
