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
import ipaddress
import logging
from typing import AsyncIterator, List, Union

from pyasic.miners.miner_factory import AnyMiner, miner_factory
from pyasic.network.net_range import MinerNetworkRange
from pyasic.settings import PyasicSettings


class MinerNetwork:
    """A class to handle a network containing miners. Handles scanning and gets miners via [`MinerFactory`][pyasic.miners.miner_factory.MinerFactory].

    Parameters:
        ip_addr: ### An IP address, range of IP addresses, or a list of IPs
            * Takes a single IP address as an `ipadddress.ipaddress()` or a string
            * Takes a string formatted as:
            ```f"{ip_range_1_start}-{ip_range_1_end}, {ip_address_1}, {ip_range_2_start}-{ip_range_2_end}, {ip_address_2}..."```
            * Also takes a list of strings or `ipaddress.ipaddress` formatted as:
            ```[{ip_address_1}, {ip_address_2}, {ip_address_3}, ...]```
        mask: A subnet mask to use when constructing the network.  Only used if `ip_addr` is a single IP.
            Defaults to /24 (255.255.255.0 or 0.0.0.255)
    """

    def __init__(
        self,
        ip_addr: Union[str, List[str], None] = None,
        mask: Union[str, int, None] = None,
    ) -> None:
        self.network = None
        self.ip_addr = ip_addr
        self.connected_miners = {}
        if isinstance(mask, str):
            if mask.startswith("/"):
                mask = mask.replace("/", "")
        self.mask = mask
        self.network = self.get_network()

    def __len__(self):
        return len([item for item in self.get_network().hosts()])

    def __repr__(self):
        return str(self.network)

    def hosts(self):
        for x in self.network.hosts():
            yield x

    def get_network(self) -> ipaddress.ip_network:
        """Get the network using the information passed to the MinerNetwork or from cache.

        Returns:
            The proper network to be able to scan.
        """
        # if we have a network cached already, use that
        if self.network:
            return self.network

            # if there is no IP address passed, default to 192.168.1.0
        if not self.ip_addr:
            self.ip_addr = "192.168.1.0"
        if "-" in self.ip_addr:
            self.network = MinerNetworkRange(self.ip_addr)
        elif isinstance(self.ip_addr, list):
            self.network = MinerNetworkRange(self.ip_addr)
        else:
            # if there is no subnet mask passed, default to /24
            if not self.mask:
                subnet_mask = "24"
            # if we do have a mask passed, use that
            else:
                subnet_mask = str(self.mask)

            # save the network and return it
            self.network = ipaddress.ip_network(
                f"{self.ip_addr}/{subnet_mask}", strict=False
            )

        logging.debug(f"{self} - (Get Network) - Found network")
        return self.network

    async def scan_network_for_miners(self) -> List[AnyMiner]:
        """Scan the network for miners, and return found miners as a list.

        Returns:
            A list of found miners.
        """
        # get the network
        local_network = self.get_network()
        logging.debug(f"{self} - (Scan Network For Miners) - Scanning")

        # clear cached miners
        miner_factory.clear_cached_miners()

        limit = asyncio.Semaphore(PyasicSettings().network_scan_threads)
        miners = await asyncio.gather(
            *[self.ping_and_get_miner(host, limit) for host in local_network.hosts()]
        )

        # remove all None from the miner list
        miners = list(filter(None, miners))
        logging.debug(
            f"{self} - (Scan Network For Miners) - Found {len(miners)} miners"
        )

        # return the miner objects
        return miners

    async def scan_network_generator(self) -> AsyncIterator[AnyMiner]:
        """
        Scan the network for miners using an async generator.

        Returns:
             An asynchronous generator containing found miners.
        """
        # get the current event loop
        loop = asyncio.get_event_loop()

        # get the network
        local_network = self.get_network()

        # create a list of scan tasks
        limit = asyncio.Semaphore(PyasicSettings().network_scan_threads)
        miners = asyncio.as_completed(
            [
                loop.create_task(self.ping_and_get_miner(host, limit))
                for host in local_network.hosts()
            ]
        )
        for miner in miners:
            try:
                yield await miner
            except TimeoutError:
                yield None

    @staticmethod
    async def ping_miner(
        ip: ipaddress.ip_address, semaphore: asyncio.Semaphore
    ) -> Union[None, ipaddress.ip_address]:
        async with semaphore:
            try:
                miner = await ping_miner(ip)
                if miner:
                    return miner
            except ConnectionRefusedError:
                tasks = [ping_miner(ip, port=port) for port in [4029, 8889]]
                for miner in asyncio.as_completed(tasks):
                    try:
                        miner = await miner
                        if miner:
                            return miner
                    except ConnectionRefusedError:
                        pass

    @staticmethod
    async def ping_and_get_miner(
        ip: ipaddress.ip_address, semaphore: asyncio.Semaphore
    ) -> Union[None, AnyMiner]:
        async with semaphore:
            try:
                miner = await ping_and_get_miner(ip)
                if miner:
                    return miner
            except ConnectionRefusedError:
                tasks = [ping_and_get_miner(ip, port=port) for port in [4029, 8889]]
                for miner in asyncio.as_completed(tasks):
                    try:
                        miner = await miner
                        if miner:
                            return miner
                    except ConnectionRefusedError:
                        pass


async def ping_miner(
    ip: ipaddress.ip_address, port=4028
) -> Union[None, ipaddress.ip_address]:
    for i in range(PyasicSettings().network_ping_retries):
        try:
            connection_fut = asyncio.open_connection(str(ip), port)
            # get the read and write streams from the connection
            reader, writer = await asyncio.wait_for(
                connection_fut, timeout=PyasicSettings().network_ping_timeout
            )
            # immediately close connection, we know connection happened
            writer.close()
            # make sure the writer is closed
            await writer.wait_closed()
            # ping was successful
            return ip
        except asyncio.exceptions.TimeoutError:
            # ping failed if we time out
            continue
        except (ConnectionRefusedError, OSError):
            # handle for other connection errors
            logging.debug(f"{str(ip)}: Connection Refused.")
            raise ConnectionRefusedError
        except Exception as e:
            logging.warning(f"{str(ip)}: Ping And Get Miner Exception: {e}")
            raise ConnectionRefusedError
    return


async def ping_and_get_miner(
    ip: ipaddress.ip_address, port=4028
) -> Union[None, AnyMiner]:
    for i in range(PyasicSettings().network_ping_retries):
        try:
            connection_fut = asyncio.open_connection(str(ip), port)
            # get the read and write streams from the connection
            reader, writer = await asyncio.wait_for(
                connection_fut, timeout=PyasicSettings().network_ping_timeout
            )
            # immediately close connection, we know connection happened
            writer.close()
            # make sure the writer is closed
            await writer.wait_closed()
            # ping was successful
            return await miner_factory.get_miner(ip)
        except asyncio.exceptions.TimeoutError:
            # ping failed if we time out
            continue
        except (ConnectionRefusedError, OSError):
            # handle for other connection errors
            logging.debug(f"{str(ip)}: Connection Refused.")
            raise ConnectionRefusedError
        except Exception as e:
            logging.warning(f"{str(ip)}: Ping And Get Miner Exception: {e}")
            raise ConnectionRefusedError
    return
