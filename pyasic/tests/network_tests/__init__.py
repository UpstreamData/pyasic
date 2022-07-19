#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import ipaddress
import unittest

from pyasic.network.net_range import MinerNetworkRange
from pyasic.network import MinerNetwork


class NetworkTest(unittest.TestCase):
    def test_net_range(self):
        net_range_str = "192.168.1.29, 192.168.1.40-192.168.1.43, 192.168.1.60"
        net_range_list = [
            "192.168.1.29",
            "192.168.1.40",
            "192.168.1.41",
            "192.168.1.42",
            "192.168.1.43",
            "192.168.1.60",
        ]

        net_1 = list(MinerNetworkRange(net_range_str).hosts())
        net_2 = list(MinerNetworkRange(net_range_list).hosts())

        correct_net = [
            ipaddress.IPv4Address("192.168.1.29"),
            ipaddress.IPv4Address("192.168.1.40"),
            ipaddress.IPv4Address("192.168.1.41"),
            ipaddress.IPv4Address("192.168.1.42"),
            ipaddress.IPv4Address("192.168.1.43"),
            ipaddress.IPv4Address("192.168.1.60"),
        ]

        self.assertTrue(net_1 == correct_net)
        self.assertTrue(net_2 == correct_net)

    def test_net(self):
        net_1_str = "192.168.1.0"
        net_1_mask = 29

        net_1 = list(MinerNetwork(net_1_str, mask=net_1_mask).get_network().hosts())

        net_2 = list(
            MinerNetwork("192.168.1.1-192.168.1.5, 192.168.1.6").get_network().hosts()
        )

        correct_net = [
            ipaddress.IPv4Address("192.168.1.1"),
            ipaddress.IPv4Address("192.168.1.2"),
            ipaddress.IPv4Address("192.168.1.3"),
            ipaddress.IPv4Address("192.168.1.4"),
            ipaddress.IPv4Address("192.168.1.5"),
            ipaddress.IPv4Address("192.168.1.6"),
        ]

        self.assertTrue(net_1 == correct_net)
        self.assertTrue(net_2 == correct_net)


if __name__ == "__main__":
    unittest.main()
