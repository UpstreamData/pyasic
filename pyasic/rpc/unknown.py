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

from pyasic.rpc.cgminer import CGMinerRPCAPI


class UnknownRPCAPI(CGMinerRPCAPI):
    """An abstraction of an API for a miner which is unknown.

    This class is designed to try to be an intersection of as many miner APIs
    and API commands as possible (API ⋂ API), to ensure that it can be used
    with as many APIs as possible.
    """

    async def switchpool(self, n: int) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("switchpool", parameters=n)

    async def enablepool(self, n: int) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("enablepool", parameters=n)

    async def disablepool(self, n: int) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("disablepool", parameters=n)

    async def addpool(self, url: str, username: str, password: str) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("addpool", parameters=f"{url},{username},{password}")

    async def removepool(self, n: int) -> dict:
        # BOS has not implemented this yet, they will in the future
        raise NotImplementedError
        # return await self.send_command("removepool", parameters=n)
