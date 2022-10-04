#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import asyncio

from pyasic.misc import Singleton


class _MinerListener:
    def __init__(self):
        self.responses = {}
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, _addr):
        m = data.decode()
        if "," in m:
            ip, mac = m.split(",")
        else:
            d = m[:-1].split("MAC")
            ip = d[0][3:]
            mac = d[1][1:]

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

        transport_14235, protocol_14235 = await loop.create_datagram_endpoint(
            lambda: _MinerListener(), local_addr=("0.0.0.0", 14235)  # noqa
        )
        transport_8888, protocol_8888 = await loop.create_datagram_endpoint(
            lambda: _MinerListener(), local_addr=("0.0.0.0", 8888)  # noqa
        )

        while True:
            if self.new_miner:
                yield self.new_miner
                self.found_miners.append(self.new_miner)
                self.new_miner = None
            if self.stop:
                transport_14235.close()
                transport_8888.close()
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
