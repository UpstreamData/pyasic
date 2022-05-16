from miners.antminer import *
from miners.whatsminer import *
from miners.avalonminer import *

from miners._backends.cgminer import CGMiner
from miners._backends.bmminer import BMMiner
from miners._backends.bosminer import BOSMiner
from miners._backends.bosminer import BOSMinerOld

from miners.unknown import UnknownMiner

from API import APIError

import asyncio
import ipaddress
import json
import logging

from settings import (
    MINER_FACTORY_GET_VERSION_RETRIES as GET_VERSION_RETRIES,
    NETWORK_PING_TIMEOUT as PING_TIMEOUT,
)

MINER_CLASSES = {
    "Antminer S9": {
        "Default": BOSMinerS9,
        "BOSMiner": BOSMinerOld,
        "BOSMiner+": BOSMinerS9,
        "BMMiner": BMMinerS9,
        "CGMiner": CGMinerS9,
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
    },
    "M21S+": {
        "Default": BTMinerM21SPlus,
        "BTMiner": BTMinerM21SPlus,
    },
    "M30S": {
        "Default": BTMinerM30S,
        "BTMiner": BTMinerM30S,
    },
    "M30S+": {
        "Default": BTMinerM30SPlus,
        "BTMiner": BTMinerM30SPlus,
    },
    "M30S++": {
        "Default": BTMinerM30SPlusPlus,
        "BTMiner": BTMinerM30SPlusPlus,
    },
    "M31S": {
        "Default": BTMinerM31S,
        "BTMiner": BTMinerM31S,
    },
    "M31S+": {
        "Default": BTMinerM31SPlus,
        "BTMiner": BTMinerM31SPlus,
    },
    "M32S": {
        "Default": BTMinerM32S,
        "BTMiner": BTMinerM32S,
    },
}


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MinerFactory(metaclass=Singleton):
    def __init__(self):
        self.miners = {}

    async def get_miner_generator(self, ips: list):
        """
        Get Miner objects from ip addresses using an async generator.

        Returns an asynchronous generator containing Miners.

        Parameters:
            ips: a list of ip addresses to get miners for.
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

    async def get_miner(self, ip: ipaddress.ip_address or str):
        """Decide a miner type using the IP address of the miner."""
        if isinstance(ip, str):
            ip = ipaddress.ip_address(ip)
        # check if the miner already exists in cache
        if ip in self.miners:
            return self.miners[ip]
        # if everything fails, the miner is already set to unknown
        miner = UnknownMiner(str(ip))
        api = None
        model = None

        # try to get the API multiple times based on retries
        for i in range(GET_VERSION_RETRIES):
            try:
                # get the API type, should be BOSMiner, CGMiner, BMMiner, BTMiner, or None
                new_model, new_api = await asyncio.wait_for(
                    self._get_miner_type(ip), timeout=PING_TIMEOUT
                )

                # keep track of the API and model we found first
                if new_api and not api:
                    api = new_api
                if new_model and not model:
                    model = new_model

                # if we find the API and model, dont need to loop anymore
                if api and model:
                    break
            except asyncio.TimeoutError:
                pass

        # make sure we have model information
        if model:
            if not api:
                api = "Default"

            # Avalonminers
            if "avalon" in model:
                if model == "avalon10":
                    miner = CGMinerAvalon1066(str(ip))
                else:
                    miner = CGMinerAvalon821(str(ip))
            else:
                if model not in MINER_CLASSES.keys():
                    miner = UnknownMiner(str(ip))
                    return miner
                if api not in MINER_CLASSES[model].keys():
                    api = "Default"
                miner = MINER_CLASSES[model][api](str(ip))

        # if we cant find a model, check if we found the API
        else:

            # return the miner base class with some API if we found it
            if api:
                if "BOSMiner+" in api:
                    miner = BOSMiner(str(ip))
                if "BOSMiner" in api:
                    miner = BOSMinerOld(str(ip))
                elif "CGMiner" in api:
                    miner = CGMiner(str(ip))
                elif "BMMiner" in api:
                    miner = BMMiner(str(ip))

        # save the miner to the cache at its IP
        self.miners[ip] = miner

        # return the miner
        return miner

    def clear_cached_miners(self):
        """Clear the miner factory cache."""
        # empty out self.miners
        self.miners = {}

    async def _get_miner_type(self, ip: ipaddress.ip_address or str) -> tuple:
        model = None
        api = None

        devdetails = None
        version = None

        try:
            data = await self._send_api_command(str(ip), "devdetails+version")

            validation = await self._validate_command(data)
            if not validation[0]:
                raise APIError(validation[1])

            devdetails = data["devdetails"][0]
            version = data["version"][0]

        except APIError as e:
            data = None

        if not data:
            try:
                devdetails = await self._send_api_command(str(ip), "devdetails")
                validation = await self._validate_command(devdetails)
                if not validation[0]:
                    version = await self._send_api_command(str(ip), "version")

                    validation = await self._validate_command(version)
                    if not validation[0]:
                        raise APIError(validation[1])
            except APIError as e:
                logging.warning(f"{ip}: API Command Error: {e}")
                return None, None

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

        if version:
            # check if there are any BMMiner strings in any of the dict keys
            if any("BMMiner" in string for string in version["VERSION"][0].keys()):
                api = "BMMiner"

            # check if there are any CGMiner strings in any of the dict keys
            elif any("CGMiner" in string for string in version["VERSION"][0].keys()):
                api = "CGMiner"

            # check if there are any BOSMiner strings in any of the dict keys
            elif any("BOSminer" in string for string in version["VERSION"][0].keys()):
                api = "BOSMiner"
                if "plus" in version["VERSION"][0]["BOSminer"]:
                    api = "BOSMiner+"

            # if all that fails, check the Description to see if it is a whatsminer
            if version.get("Description") and "whatsminer" in version.get("Description"):
                api = "BTMiner"
        if version and not model:
            if (
                "VERSION" in version.keys()
                and version.get("VERSION")
                and not version.get("VERSION") == []
            ):
                model = version["VERSION"][0]["Type"]

        if model:
            if "V" in model:
                model = model.split("V")[0]
            if "Bitmain " in model:
                model = model.replace("Bitmain ", "")

        return model, api

    async def _validate_command(self, data: dict) -> tuple:
        """Check if the returned command output is correctly formatted."""
        # check if the data returned is correct or an error
        if not data:
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

    async def _send_api_command(self, ip: ipaddress.ip_address or str, command: str):
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(ip), 4028)
        except OSError as e:
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
            # fix an error with a bmminer return not having a specific comma that breaks json.loads()
            str_data = str_data.replace("}{", "},{")
            # parse the json
            data = json.loads(str_data)
        # handle bad json
        except json.decoder.JSONDecodeError as e:
            # raise APIError(f"Decode Error: {data}")
            data = None

        # close the connection
        writer.close()
        await writer.wait_closed()

        return data
