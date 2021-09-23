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


class CGMiner(API):
    def __init__(self, ip, port):
        super().__init__(ip, port)


class BMMiner(API):
    def __init__(self, ip, port):
        super().__init__(ip, port)

    def version(self):
        return self.send_command("version")

    def config(self):
        return self.send_command("config")

    def summary(self):
        return self.send_command("summary")

    def pools(self):
        return self.send_command("pools")

    def devs(self):
        return self.send_command("devs")

    def edevs(self):
        return self.send_command("edevs")

    def pgacount(self):
        return self.send_command("pgacount")

    def notify(self):
        return self.send_command("notify")

    def devdetails(self):
        return self.send_command("devdetails")

    def stats(self):
        return self.send_command("stats")

    def estats(self):
        return self.send_command("estats")

    def check(self):
        return self.send_command("check")

    def coin(self):
        return self.send_command("coin")

    def asccount(self):
        return self.send_command("asccount")

    def lcd(self):
        return self.send_command("lcd")



class BOSMiner(API):
    def __init__(self, ip, port):
        super().__init__(ip, port)

    def asccount(self):
        return self.send_command("asccount")

    def devdetails(self):
        return self.send_command("devdetails")

    def devs(self):
        return self.send_command("devs")

    def edevs(self):
        return self.send_command("edevs")

    def pools(self):
        return self.send_command("pools")

    def summary(self):
        return self.send_command("summary")

    def stats(self):
        return self.send_command("stats")

    def version(self):
        return self.send_command("version")

    def estats(self):
        return self.send_command("estats")

    def check(self):
        return self.send_command("check")

    def coin(self):
        return self.send_command("coin")

    def lcd(self):
        return self.send_command("lcd")

    def fans(self):
        return self.send_command("fans")

    def tempctrl(self):
        return self.send_command("tempctrl")

    def temps(self):
        return self.send_command("temps")

    def tunerstatus(self):
        return self.send_command("tunerstatus")
