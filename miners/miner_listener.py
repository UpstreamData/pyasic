import asyncio


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class _MinerListener:
    def __init__(self):
        self.responses = {}

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        m = data.decode()
        ip, mac = m.split(",")
        new_miner = {"IP": ip, "MAC": mac.upper()}
        MinerListener().new_miner = new_miner


class MinerListener(metaclass=Singleton):
    def __init__(self):
        self.found_miners = []
        self.new_miner = None

    async def listen(self):
        loop = asyncio.get_running_loop()

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: _MinerListener(), local_addr=("0.0.0.0", 14235)
        )

        while True:
            if self.new_miner:
                yield self.new_miner
                self.found_miners.append(self.new_miner)
                self.new_miner = None
            await asyncio.sleep(0)


async def main():
    async for miner in MinerListener().listen():
        print(miner)


if __name__ == "__main__":
    asyncio.run(main())
