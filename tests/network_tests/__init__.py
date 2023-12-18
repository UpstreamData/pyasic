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

import ipaddress
import unittest

from pyasic.network import MinerNetwork


class NetworkTest(unittest.TestCase):
    def test_net_range(self):
        net_range_str = ["192.168.1.29", "192.168.1.40-43", "192.168.1.60"]
        net_range_list = [
            "192.168.1.29",
            "192.168.1.40",
            "192.168.1.41",
            "192.168.1.42",
            "192.168.1.43",
            "192.168.1.60",
        ]

        net_1 = list(MinerNetwork.from_list(net_range_list).hosts)
        net_2 = list(MinerNetwork.from_list(net_range_str).hosts)

        correct_net = [
            ipaddress.IPv4Address("192.168.1.29"),
            ipaddress.IPv4Address("192.168.1.40"),
            ipaddress.IPv4Address("192.168.1.41"),
            ipaddress.IPv4Address("192.168.1.42"),
            ipaddress.IPv4Address("192.168.1.43"),
            ipaddress.IPv4Address("192.168.1.60"),
        ]

        self.assertEqual(net_1, correct_net)
        self.assertEqual(net_2, correct_net)

    def test_net(self):
        net_1_str = "192.168.1.0"
        net_1_mask = "/29"

        net_1 = list(MinerNetwork.from_subnet(net_1_str + net_1_mask).hosts)

        net_2 = list(MinerNetwork.from_list(["192.168.1.1-5", "192.168.1.6"]).hosts)

        correct_net = [
            ipaddress.IPv4Address("192.168.1.1"),
            ipaddress.IPv4Address("192.168.1.2"),
            ipaddress.IPv4Address("192.168.1.3"),
            ipaddress.IPv4Address("192.168.1.4"),
            ipaddress.IPv4Address("192.168.1.5"),
            ipaddress.IPv4Address("192.168.1.6"),
        ]

        self.assertEqual(net_1, correct_net)
        self.assertEqual(net_2, correct_net)

    def test_net_defaults(self):
        net = MinerNetwork.from_subnet("192.168.1.1/24")
        self.assertEqual(
            net.hosts, list(ipaddress.ip_network("192.168.1.0/24").hosts())
        )


if __name__ == "__main__":
    unittest.main()
