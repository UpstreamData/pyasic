import ipaddress
import asyncio
from miners.miner_factory import MinerFactory
from settings import NETWORK_PING_RETRIES as PING_RETRIES, NETWORK_PING_TIMEOUT as PING_TIMEOUT, NETWORK_SCAN_THREADS as SCAN_THREADS


class MinerNetwork:
    def __init__(self, ip_addr: str or None = None, mask: str or int or None = None) -> None:
        self.network = None
        self.miner_factory = MinerFactory()
        self.ip_addr = ip_addr
        self.connected_miners = {}
        self.mask = mask

    def __len__(self):
        return len([item for item in self.get_network().hosts()])

    def get_network(self) -> ipaddress.ip_network:
        """Get the network using the information passed to the MinerNetwork or from cache."""
        if self.network:
            return self.network
        if not self.ip_addr:
            default_gateway = "192.168.1.0"
        else:
            default_gateway = self.ip_addr
        if self.mask:
            subnet_mask = str(self.mask)
        else:
            subnet_mask = "24"
        return ipaddress.ip_network(f"{default_gateway}/{subnet_mask}", strict=False)

    async def scan_network_for_miners(self) -> None or list:
        """Scan the network for miners, and """
        local_network = self.get_network()
        print(f"Scanning {local_network} for miners...")
        scan_tasks = []
        miner_ips = []
        for host in local_network.hosts():
            if len(scan_tasks) < SCAN_THREADS:
                scan_tasks.append(self.ping_miner(host))
            else:
                miner_ips_scan = await asyncio.gather(*scan_tasks)
                miner_ips.extend(miner_ips_scan)
                scan_tasks = []
        miner_ips_scan = await asyncio.gather(*scan_tasks)
        miner_ips.extend(miner_ips_scan)
        miner_ips = list(filter(None, miner_ips))
        print(f"Found {len(miner_ips)} connected miners...")
        create_miners_tasks = []
        self.miner_factory.clear_cached_miners()
        for miner_ip in miner_ips:
            create_miners_tasks.append(self.miner_factory.get_miner(miner_ip))
        miners = await asyncio.gather(*create_miners_tasks)
        return miners


    async def scan_network_generator(self):
        loop = asyncio.get_event_loop()
        local_network = self.get_network()
        scan_tasks = []
        for host in local_network.hosts():
            if len(scan_tasks) >= SCAN_THREADS:
                scanned = asyncio.as_completed(scan_tasks)
                scan_tasks = []
                for miner in scanned:
                    yield await miner
            scan_tasks.append(loop.create_task(self.ping_miner(host)))
        scanned = asyncio.as_completed(scan_tasks)
        for miner in scanned:
            yield await miner


    @staticmethod
    async def ping_miner(ip: ipaddress.ip_address) -> None or ipaddress.ip_address:
        for i in range(PING_RETRIES):
            connection_fut = asyncio.open_connection(str(ip), 4028)
            try:
                # get the read and write streams from the connection
                reader, writer = await asyncio.wait_for(connection_fut, timeout=PING_TIMEOUT)
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
                print(f"{str(ip)}: Connection Refused.")
            # ping failed, likely with an exception
            except Exception as e:
                print(e)
            continue
        return
