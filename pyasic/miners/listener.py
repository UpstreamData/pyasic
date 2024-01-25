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

    def connection_made(self, transport):
        self.transport = transport

    @staticmethod
    def datagram_received(data, _addr):
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


class MinerListener:
    def __init__(self, bind_addr: str = "0.0.0.0"):
        self.found_miners = []
        self.new_miner = None
        self.stop = False
        self.bind_addr = bind_addr

    async def listen(self):
        self.stop = False

        loop = asyncio.get_running_loop()

        transport_14235, _ = await loop.create_datagram_endpoint(
            MinerListenerProtocol, local_addr=(self.bind_addr, 14235)
        )
        transport_8888, _ = await loop.create_datagram_endpoint(
            MinerListenerProtocol, local_addr=(self.bind_addr, 8888)
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
