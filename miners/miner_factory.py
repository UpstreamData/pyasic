from miners.antminer.S9.bosminer import BOSMinerS9
from miners.antminer.S9.bmminer import BMMinerS9
from miners.antminer.S9.cgminer import CGMinerS9

from miners.antminer.T9.hive import HiveonT9
from miners.antminer.T9.cgminer import CGMinerT9
from miners.antminer.T9.bmminer import BMMinerT9

from miners.antminer.X17.bosminer import BOSMinerX17
from miners.antminer.X17.bmminer import BMMinerX17
from miners.antminer.X17.cgminer import CGMinerX17

from miners.antminer.X19.bmminer import BMMinerX19
from miners.antminer.X19.cgminer import CGMinerX19
from miners.antminer.X19.bosminer import BOSMinerX19

from miners.whatsminer.M20 import BTMinerM20
from miners.whatsminer.M21 import BTMinerM21
from miners.whatsminer.M30 import BTMinerM30
from miners.whatsminer.M31 import BTMinerM31
from miners.whatsminer.M32 import BTMinerM32

from miners.avalonminer.Avalon8 import CGMinerAvalon8
from miners.avalonminer.Avalon10 import CGMinerAvalon10

from miners.cgminer import CGMiner
from miners.bmminer import BMMiner
from miners.bosminer import BOSMiner

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


class MinerFactory:
    _instance = None

    def __init__(self):
        self.miners = {}

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(MinerFactory, cls).__new__(cls)
        return cls._instance

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

    async def get_miner(self, ip: ipaddress.ip_address):
        """Decide a miner type using the IP address of the miner."""
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
            # check if the miner is an Antminer
            if "Antminer" in model:
                # S9 logic
                if "Antminer S9" in model:
                    # handle the different API types
                    if not api:
                        logging.warning(
                            f"{str(ip)}: No API data found,  using BraiinsOS."
                        )
                        miner = BOSMinerS9(str(ip))
                    elif "BOSMiner" in api:
                        miner = BOSMinerS9(str(ip))
                    elif "CGMiner" in api:
                        miner = CGMinerS9(str(ip))
                    elif "BMMiner" in api:
                        miner = BMMinerS9(str(ip))

                elif "Antminer T9" in model:
                    if "BMMiner" in api:
                        if "Hiveon" in model:
                            # hiveOS, return T9 Hive
                            miner = HiveonT9(str(ip))
                        else:
                            miner = BMMinerT9(str(ip))
                    elif "CGMiner" in api:
                        miner = CGMinerT9(str(ip))

                # X17 model logic
                elif "17" in model:
                    # handle the different API types
                    if "BOSMiner" in api:
                        miner = BOSMinerX17(str(ip))
                    elif "CGMiner" in api:
                        miner = CGMinerX17(str(ip))
                    elif "BMMiner" in api:
                        miner = BMMinerX17(str(ip))

                # X19 logic
                elif "19" in model:
                    # handle the different API types
                    if "BOSMiner" in api:
                        miner = BOSMinerX19(str(ip))
                    if "CGMiner" in api:
                        miner = CGMinerX19(str(ip))
                    elif "BMMiner" in api:
                        miner = BMMinerX19(str(ip))

            # Avalonminers
            elif "avalon" in model:
                if model == "avalon10":
                    miner = CGMinerAvalon10(str(ip))
                else:
                    miner = CGMinerAvalon8(str(ip))

            # Whatsminers
            elif "M20" in model:
                miner = BTMinerM20(str(ip))
            elif "M21" in model:
                miner = BTMinerM21(str(ip))
            elif "M30" in model:
                miner = BTMinerM30(str(ip))
            elif "M31" in model:
                miner = BTMinerM31(str(ip))
            elif "M32" in model:
                miner = BTMinerM32(str(ip))

        # if we cant find a model, check if we found the API
        else:

            # return the miner base class with some API if we found it
            if api:
                if "BOSMiner" in api:
                    miner = BOSMiner(str(ip))
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
            logging.warning(f"{ip}: API Command Error: {e}")
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

            # if all that fails, check the Description to see if it is a whatsminer
        elif version.get("Description") and "whatsminer" in version.get("Description"):
            api = "BTMiner"

        if version and not model:
            if "VERSION" in version.keys() and not version["DEVDETAILS"] == []:
                model = version["VERSION"][0]["Type"]

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
