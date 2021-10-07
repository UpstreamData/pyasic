from miners.bosminer import BOSminer
from miners.bmminer import BMMiner
from miners.cgminer import CGMiner
from API import APIError
import asyncio
import ipaddress
import json

class MinerFactory:
    async def get_miner(self, ip: ipaddress.ip_address):
        version_data = await self._get_version_data(ip)
        version = None
        if version_data:
            version = list(version_data['VERSION'][0].keys())[0]
        if version:
            if version == "BOSminer":
                return BOSminer(str(ip))
            elif version == "CGMiner":
                return CGMiner(str(ip))
            elif version == "BMMiner":
                return BMMiner(str(ip))
        return f"Unknown: {str(ip)}"

    async def _get_version_data(self, ip: ipaddress.ip_address):
        try:
            # get reader and writer streams
            reader, writer = await asyncio.open_connection(str(ip), 4028)

            # create the command
            cmd = {"command": "version"}

            # send the command
            writer.write(json.dumps(cmd).encode('utf-8'))
            await writer.drain()

            # instantiate data
            data = b""

            # loop to receive all the data
            while True:
                d = await reader.read(4096)
                if not d:
                    break
                data += d

            data = json.loads(data.decode('utf-8')[:-1])

            # close the connection
            writer.close()
            await writer.wait_closed()

            # check if the data returned is correct or an error
            # if status isn't a key, it is a multicommand
            if "STATUS" not in data.keys():
                for key in data.keys():
                    # make sure not to try to turn id into a dict
                    if not key == "id":
                        # make sure they succeeded
                        if data[key][0]["STATUS"][0]["STATUS"] not in ["S", "I"]:
                            # this is an error
                            raise APIError(data["STATUS"][0]["Msg"])
            else:
                # make sure the command succeeded
                if data["STATUS"][0]["STATUS"] not in ("S", "I"):
                    # this is an error
                    raise APIError(data["STATUS"][0]["Msg"])

            # return the data
            return data
        except Exception as e:
            print(e)
            return None
