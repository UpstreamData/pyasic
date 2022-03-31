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
                for host in network.hosts():
                    self.host_ips.append(host)

    def hosts(self):
        for x in self.host_ips:
            yield x
