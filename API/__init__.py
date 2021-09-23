import asyncio
import json


class APIError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return f"{self.message}"
        else:
            return "Incorrect API parameters."


class BaseMinerAPI:
    def __init__(self, ip, port):
        self.port = port
        self.ip = ip

    async def send_command(self, command, parameters=None):
        # get reader and writer streams
        reader, writer = await asyncio.open_connection(self.ip, self.port)

        # create the command
        cmd = {"command": command}
        if parameters:
            cmd["parameters"] = parameters

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
        if not data["STATUS"][0]["STATUS"] in ("S", "I"):
            # this is an error
            raise APIError(data["STATUS"][0]["Msg"])

        # return the data
        return data
