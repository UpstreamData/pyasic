import ipaddress
from typing import Union

class MinerNetworkRange:
    """A MinerNetwork that takes a range of IP addresses.

    :param ip_range: A range of IP addresses to put in the network, or a list of IPs
        Takes a string formatted as
        {ip_range_1_start}-{ip_range_1_end}, {ip_range_2_start}-{ip_range_2_end}
        Also takes a list of strings formatted as
        [{ip1}. {ip2}, {ip3}, ...]

    """

    def __init__(self, ip_range: Union[str, list]):
        self.host_ips = []
        if isinstance(ip_range, str):
            ip_ranges = ip_range.replace(" ", "").split(",")
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
        elif isinstance(ip_range, list):
            self.host_ips = ip_range

    def hosts(self):
        for x in self.host_ips:
            yield x
