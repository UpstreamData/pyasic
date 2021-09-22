import asyncio
import json


class API:
    def __init__(self, port, ip):
        self.port = port
        self.ip = ip

    async def send_command(self, command):
        # get reader and writer streams
        reader, writer = await asyncio.open_connection(self.ip, self.port)

        # send the command
        writer.write(json.dumps({"command": command}).encode('utf-8'))
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

        # return the data
        return data
