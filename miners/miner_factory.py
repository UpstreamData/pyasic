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

from miners.whatsminer.M20 import BTMinerM20
from miners.whatsminer.M21 import BTMinerM21
from miners.whatsminer.M30 import BTMinerM30
from miners.whatsminer.M31 import BTMinerM31
from miners.whatsminer.M32 import BTMinerM32

from miners.avalonminer import CGMinerAvalon

from miners.cgminer import CGMiner
from miners.bmminer import BMMiner
from miners.bosminer import BOSMiner

from miners.unknown import UnknownMiner

from API import APIError

import asyncio
import ipaddress
import json

from settings import MINER_FACTORY_GET_VERSION_RETRIES as GET_VERSION_RETRIES


class MinerFactory:
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
            # get the API type, should be BOSMiner, CGMiner, BMMiner, BTMiner, or None
            api = await self._get_api_type(ip)
            # if we find the API type, dont need to loop anymore
            if api:
                break

        # try to get the model multiple times based on retries
        for i in range(GET_VERSION_RETRIES):
            # get the model, should return some miner model type, e.g. Antminer S9
            model = await self._get_miner_model(ip)
            # if we find the model type, dont need to loop anymore
            if model:
                break
        # make sure we have model information
        if model:

            # check if the miner is an Antminer
            if "Antminer" in model:

                # S9 logic
                if "Antminer S9" in model:

                    # handle the different API types
                    if not api:
                        print(ip)
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
                    if "CGMiner" in api:
                        miner = CGMinerX19(str(ip))
                    elif "BMMiner" in api:
                        miner = BMMinerX19(str(ip))

            # Avalonminer V8
            elif "avalon" in model:
                miner = CGMinerAvalon(str(ip))

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

    async def _get_miner_model(self, ip: ipaddress.ip_address or str) -> str or None:
        # instantiate model as being nothing if getting it fails
        model = None

        # try block in case of APIError or OSError 121 (Semaphore timeout)
        try:

            # send the devdetails command to the miner (will fail with no boards/devices)
            data = await self._send_api_command(str(ip), "devdetails")
            # sometimes data is b'', check for that
            if data:
                # status check, make sure the command succeeded
                if data.get("STATUS"):
                    if not isinstance(data["STATUS"], str):
                        # if status is E, its an error
                        if data["STATUS"][0].get("STATUS") not in ["I", "S"]:

                            # try an alternate method if devdetails fails
                            data = await self._send_api_command(str(ip), "version")

                            # make sure we have data
                            if data:
                                # check the keys are there to get the version
                                if data.get("VERSION"):
                                    if data["VERSION"][0].get("Type"):
                                        # save the model to be returned later
                                        model = data["VERSION"][0]["Type"]
                        else:
                            # make sure devdetails actually contains data, if its empty, there are no devices
                            if "DEVDETAILS" in data.keys() and not data["DEVDETAILS"] == []:

                                # check for model, for most miners
                                if not data["DEVDETAILS"][0]["Model"] == "":
                                    # model of most miners
                                    model = data["DEVDETAILS"][0]["Model"]

                                # if model fails, try driver
                                else:
                                    # some avalonminers have model in driver
                                    model = data["DEVDETAILS"][0]["Driver"]
                    else:
                        # if all that fails, try just version
                        data = await self._send_api_command(str(ip), "version")
                        if "VERSION" in data.keys():
                            model = data["VERSION"][0]["Type"]
                        else:
                            print(data)

            return model

        # if there are errors, we just return None
        except APIError as e:
            print(e)
        except OSError as e:
            print(e)
        return model

    async def _send_api_command(self, ip: ipaddress.ip_address or str, command: str):
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(ip), 4028)
        except OSError as e:
            print(e)
            return {}

        # create the command
        cmd = {"command": command}

        # send the command
        writer.write(json.dumps(cmd).encode('utf-8'))
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

        try:
            # some json from the API returns with a null byte (\x00) on the end
            if data.endswith(b"\x00"):
                # handle the null byte
                str_data = data.decode('utf-8')[:-1]
            else:
                # no null byte
                str_data = data.decode('utf-8')
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

    async def _get_api_type(self, ip: ipaddress.ip_address or str) -> dict or None:
        """Get data on the version of the miner to return the right miner."""
        # instantiate API as None in case something fails
        api = None

        # try block to handle OSError 121 (Semaphore timeout)
        try:
            # try the version command,works on most miners
            data = await self._send_api_command(str(ip), "version")

            # if we got data back, try to parse it
            if data:
                # make sure the command succeeded
                if data.get("STATUS") and not data.get("STATUS") == "E":
                    if data["STATUS"][0].get("STATUS") in ["I", "S"]:

                        # check if there are any BMMiner strings in any of the dict keys
                        if any("BMMiner" in string for string in data["VERSION"][0].keys()):
                            api = "BMMiner"

                        # check if there are any CGMiner strings in any of the dict keys
                        elif any("CGMiner" in string for string in data["VERSION"][0].keys()):
                            api = "CGMiner"

                        # check if there are any BOSMiner strings in any of the dict keys
                        elif any("BOSminer" in string for string in data["VERSION"][0].keys()):
                            api = "BOSMiner"

                # if all that fails, check the Description to see if it is a whatsminer
                elif data.get("Description") and "whatsminer" in data.get("Description"):
                    api = "BTMiner"

            # return the API if we found it
            if api:
                return api

        # if there are errors, return None
        except OSError as e:
            if e.winerror == 121:
                return None
            else:
                print(ip, e)
        return None
