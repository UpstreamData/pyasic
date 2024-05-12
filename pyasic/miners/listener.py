# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------

import asyncio


class MinerListenerProtocol(asyncio.Protocol):
    def __init__(self):
        self.responses = {}
        self.transport = None
        self.new_miner = None

    async def get_new_miner(self):
        try:
            while self.new_miner is None:
                await asyncio.sleep(0)
            return self.new_miner
        finally:
            self.new_miner = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, _addr):
        if data == b"OK\x00\x00\x00\x00\x00\x00\x00\x00":
            return
        m = data.decode()
        if "," in m:
            ip, mac = m.split(",")
            if "/" in ip:
                ip = ip.replace("[", "").split("/")[0]
        else:
            d = m[:-1].split("MAC")
            ip = d[0][3:]
            mac = d[1][1:]

        self.new_miner = {"IP": ip, "MAC": mac.upper()}

    def connection_lost(self, _):
        pass


class MinerListener:
    def __init__(self, bind_addr: str = "0.0.0.0"):
        self.found_miners = []
        self.stop = asyncio.Event()
        self.bind_addr = bind_addr

    async def listen(self):
        loop = asyncio.get_running_loop()

        transport_14235, protocol_14235 = await loop.create_datagram_endpoint(
            MinerListenerProtocol, local_addr=(self.bind_addr, 14235)
        )
        transport_8888, protocol_8888 = await loop.create_datagram_endpoint(
            MinerListenerProtocol, local_addr=(self.bind_addr, 8888)
        )
        try:
            while not self.stop.is_set():
                tasks = [
                    asyncio.create_task(protocol_14235.get_new_miner()),
                    asyncio.create_task(protocol_8888.get_new_miner()),
                ]
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for t in tasks:
                    if t.done():
                        yield t.result()

        finally:
            transport_14235.close()
            transport_8888.close()

    async def cancel(self):
        self.stop = True
