import ipaddress
import asyncio
import logging
from typing import Union

from pyasic.network.net_range import MinerNetworkRange
from pyasic.miners.miner_factory import MinerFactory
from pyasic.settings import (
    NETWORK_PING_RETRIES as PING_RETRIES,
    NETWORK_PING_TIMEOUT as PING_TIMEOUT,
    NETWORK_SCAN_THREADS as SCAN_THREADS,
)


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
        self, ip_addr: Union[str, None] = None, mask: Union[str, int, None] = None
    ) -> None:
        self.network = None
        self.ip_addr = ip_addr
        self.connected_miners = {}
        if isinstance(mask, str):
            if mask.startswith("/"):
                mask = mask.replace("/", "")
        self.mask = mask

    def __len__(self):
        return len([item for item in self.get_network().hosts()])

    def __repr__(self):
        return str(self.network)

    def get_network(self) -> ipaddress.ip_network:
        """Get the network using the information passed to the MinerNetwork or from cache."""
        # if we have a network cached already, use that
        if self.network:
            return self.network

        if "-" in self.ip_addr:
            self.network = MinerNetworkRange(self.ip_addr)
        elif isinstance(self.ip_addr, list):
            self.network = MinerNetworkRange(self.ip_addr)
        else:
            # if there is no IP address passed, default to 192.168.1.0
            if not self.ip_addr:
                default_gateway = "192.168.1.0"
            # if we do have an IP address passed, use that
            else:
                default_gateway = self.ip_addr

            # if there is no subnet mask passed, default to /24
            if not self.mask:
                subnet_mask = "24"
            # if we do have a mask passed, use that
            else:
                subnet_mask = str(self.mask)

            # save the network and return it
            self.network = ipaddress.ip_network(
                f"{default_gateway}/{subnet_mask}", strict=False
            )
        return self.network

    async def scan_network_for_miners(self) -> None or list:
        """Scan the network for miners, and return found miners as a list."""
        # get the network
        local_network = self.get_network()
        print(f"Scanning {local_network} for miners...")

        # clear cached miners
        MinerFactory().clear_cached_miners()

        # create a list of tasks and miner IPs
        scan_tasks = []
        miners = []

        # for each IP in the network
        for host in local_network.hosts():

            # make sure we don't exceed the allowed async tasks
            if len(scan_tasks) < SCAN_THREADS:
                # add the task to the list
                scan_tasks.append(self.ping_and_get_miner(host))
            else:
                # run the scan tasks
                miners_scan = await asyncio.gather(*scan_tasks)
                # add scanned miners to the list of found miners
                miners.extend(miners_scan)
                # empty the task list
                scan_tasks = []
        # do a final scan to empty out the list
        miners_scan = await asyncio.gather(*scan_tasks)
        miners.extend(miners_scan)

        # remove all None from the miner list
        miners = list(filter(None, miners))
        print(f"Found {len(miners)} connected miners...")

        # return the miner objects
        return miners

    async def scan_network_generator(self):
        """
        Scan the network for miners using an async generator.

        Returns an asynchronous generator containing found miners.
        """
        # get the current event loop
        loop = asyncio.get_event_loop()

        # get the network
        local_network = self.get_network()

        # create a list of scan tasks
        scan_tasks = []

        # for each ip on the network, loop through and scan it
        for host in local_network.hosts():
            # make sure we don't exceed the allowed async tasks
            if len(scan_tasks) >= SCAN_THREADS:
                # scanned is a loopable list of awaitables
                scanned = asyncio.as_completed(scan_tasks)
                # when we scan, empty the scan tasks
                scan_tasks = []

                # yield miners as they are scanned
                for miner in scanned:
                    yield await miner

            # add the ping to the list of tasks if we dont scan
            scan_tasks.append(loop.create_task(self.ping_and_get_miner(host)))

        # do one last scan at the end to close out the list
        scanned = asyncio.as_completed(scan_tasks)
        for miner in scanned:
            yield await miner

    @staticmethod
    async def ping_miner(ip: ipaddress.ip_address) -> None or ipaddress.ip_address:
        return await ping_miner(ip)

    @staticmethod
    async def ping_and_get_miner(
        ip: ipaddress.ip_address,
    ) -> None or ipaddress.ip_address:
        return await ping_and_get_miner(ip)


async def ping_miner(
    ip: ipaddress.ip_address, port=4028
) -> None or ipaddress.ip_address:
    for i in range(PING_RETRIES):
        connection_fut = asyncio.open_connection(str(ip), port)
        try:
            # get the read and write streams from the connection
            reader, writer = await asyncio.wait_for(
                connection_fut, timeout=PING_TIMEOUT
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
        except ConnectionRefusedError:
            # handle for other connection errors
            logging.debug(f"{str(ip)}: Connection Refused.")
        # ping failed, likely with an exception
        except Exception as e:
            logging.warning(f"{str(ip)}: {e}")
        continue
    return


async def ping_and_get_miner(
    ip: ipaddress.ip_address, port=4028
) -> None or ipaddress.ip_address:
    for i in range(PING_RETRIES):
        connection_fut = asyncio.open_connection(str(ip), port)
        try:
            # get the read and write streams from the connection
            reader, writer = await asyncio.wait_for(
                connection_fut, timeout=PING_TIMEOUT
            )
            # immediately close connection, we know connection happened
            writer.close()
            # make sure the writer is closed
            await writer.wait_closed()
            # ping was successful
            return await MinerFactory().get_miner(ip)
        except asyncio.exceptions.TimeoutError:
            # ping failed if we time out
            continue
        except ConnectionRefusedError:
            # handle for other connection errors
            logging.debug(f"{str(ip)}: Connection Refused.")
        # ping failed, likely with an exception
        except Exception as e:
            logging.warning(f"{str(ip)}: {e}")
        continue
    return
