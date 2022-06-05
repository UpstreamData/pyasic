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
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, _addr):
        m = data.decode()
        ip, mac = m.split(",")
        new_miner = {"IP": ip, "MAC": mac.upper()}
        MinerListener().new_miner = new_miner

    def connection_lost(self, _):
        pass


class MinerListener(metaclass=Singleton):
    def __init__(self):
        self.found_miners = []
        self.new_miner = None
        self.stop = False

    async def listen(self):
        self.stop = False

        loop = asyncio.get_running_loop()

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: _MinerListener(), local_addr=("0.0.0.0", 14235)  # noqa
        )

        while True:
            if self.new_miner:
                yield self.new_miner
                self.found_miners.append(self.new_miner)
                self.new_miner = None
            if self.stop:
                transport.close()
                break
            await asyncio.sleep(0)

    async def cancel(self):
        self.stop = True


async def main():
    await asyncio.gather(run(), cancel())


async def run():
    async for miner in MinerListener().listen():
        print(miner)


async def cancel():
    await asyncio.sleep(60)
    await MinerListener().cancel()


if __name__ == "__main__":
    asyncio.run(main())
