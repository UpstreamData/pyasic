from miners.antminer.S9.bos import BOSMinerS9
from miners.antminer.X17.bos import BOSMinerX17

from miners.whatsminer.M20 import BTMinerM20
from miners.whatsminer.M21 import BTMinerM21
from miners.whatsminer.M30 import BTMinerM30
from miners.whatsminer.M31 import BTMinerM31
from miners.whatsminer.M32 import BTMinerM32

from miners.bosminer import BOSminer
from miners.bmminer import BMMiner
from miners.cgminer import CGMiner
from miners.btminer import BTMiner
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
        loop = asyncio.get_event_loop()
        scan_tasks = []
        for miner in ips:
            scan_tasks.append(loop.create_task(self.get_miner(miner)))
        scanned = asyncio.as_completed(scan_tasks)
        for miner in scanned:
            yield await miner

    async def get_miner(self, ip: ipaddress.ip_address) -> BOSminer or CGMiner or BMMiner or BTMiner or UnknownMiner:
        """Decide a miner type using the IP address of the miner."""
        # check if the miner already exists in cache
        if ip in self.miners:
            return self.miners[ip]
        miner = UnknownMiner(str(ip))
        api = None
        for i in range(GET_VERSION_RETRIES):
            api = await self._get_api_type(ip)
            if api:
                break
        model = None
        for i in range(GET_VERSION_RETRIES):
            model = await self._get_miner_model(ip)
            if model:
                break
        if model:
            if "Antminer" in model:
                if model == "Antminer S9":
                    if "BOSMiner" in api:
                        miner = BOSMinerS9(str(ip))
                    elif "CGMiner" in api:
                        miner = CGMiner(str(ip))
                    elif "BMMiner" in api:
                        miner = BMMiner(str(ip))
                elif "17" in model:
                    if "BOSMiner" in api:
                        miner = BOSMinerX17(str(ip))
                    elif "CGMiner" in api:
                        miner = CGMiner(str(ip))
                    elif "BMMiner" in api:
                        miner = BMMiner(str(ip))
                elif "19" in model:
                    if "CGMiner" in api:
                        miner = CGMiner(str(ip))
                    elif "BMMiner" in api:
                        miner = BMMiner(str(ip))
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
        self.miners[ip] = miner
        return miner

    def clear_cached_miners(self):
        """Clear the miner factory cache."""
        self.miners = {}

    async def _get_miner_model(self, ip: ipaddress.ip_address or str) -> dict or None:
        model = None
        try:
            data = await self._send_api_command(str(ip), "devdetails")
            if data.get("STATUS"):
                if data["STATUS"][0].get("STATUS") not in ["I", "S"]:
                    try:
                        data = await self._send_api_command(str(ip), "version")
                        model = data["VERSION"][0]["Type"]
                    except:
                        print(f"Get Model Exception: {ip}")
                else:
                    model = data["DEVDETAILS"][0]["Model"]
            if model:
                return model
        except OSError as e:
            if e.winerror == 121:
                return None
            else:
                print(ip, e)
        return None

    async def _send_api_command(self, ip: ipaddress.ip_address or str, command: str):
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(ip), 4028)
        # handle OSError 121
        except OSError as e:
            if e.winerror == "121":
                print("Semaphore Timeout has Expired.")
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
            parsed_data = json.loads(str_data)
        # handle bad json
        except json.decoder.JSONDecodeError as e:
            print(e)
            raise APIError(f"Decode Error: {data}")
        data = parsed_data

        # close the connection
        writer.close()
        await writer.wait_closed()

        return data


    async def _get_api_type(self, ip: ipaddress.ip_address or str) -> dict or None:
        """Get data on the version of the miner to return the right miner."""
        api = None
        try:
            data = await self._send_api_command(str(ip), "version")
            if data.get("STATUS") and not data.get("STATUS") == "E":
                if data["STATUS"][0].get("STATUS") in ["I", "S"]:
                    if "BMMiner" in data["VERSION"][0].keys():
                        api = "BMMiner"
                    elif "CGMiner" in data["VERSION"][0].keys():
                        api = "CGMiner"
                    elif "BOSminer" in data["VERSION"][0].keys() or "BOSminer+" in data["VERSION"][0].keys():
                        api = "BOSMiner"
            elif data.get("Description") and "whatsminer" in data.get("Description"):
                api = "BTMiner"
            if api:
                return api
        except OSError as e:
            if e.winerror == 121:
                return None
            else:
                print(ip, e)
        return None
