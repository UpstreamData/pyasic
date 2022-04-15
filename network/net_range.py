import ipaddress


class MinerNetworkRange:
    """A MinerNetwork that takes a range of IP addresses.

    :param ip_range: A range of IP addresses to put in the network.
        Takes a string formatted as
        {ip_range_1_start}-{ip_range_1_end}, {ip_range_2_start}-{ip_range_2_end}

    """

    def __init__(self, ip_range: str):
        ip_ranges = ip_range.replace(" ", "").split(",")
        self.host_ips = []
        for item in ip_ranges:
            start, end = item.split("-")
            start_ip = ipaddress.ip_address(start)
            end_ip = ipaddress.ip_address(end)
            networks = ipaddress.summarize_address_range(start_ip, end_ip)
            for network in networks:
                self.host_ips.append(network.network_address)
                for host in network.hosts():
                    if host not in self.host_ips:
                        self.host_ips.append(host)
                if network.broadcast_address not in self.host_ips:
                    self.host_ips.append(network.broadcast_address)

    def hosts(self):
        for x in self.host_ips:
            yield x
