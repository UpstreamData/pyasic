import ipaddress

from network.net_range import MinerNetworkRange
from network import MinerNetwork


def test_network():
    net_range_str = "192.168.1.29, 192.168.1.40-192.168.1.43, 192.168.1.60"
    net_range_list = [
        "192.168.1.29",
        "192.168.1.40",
        "192.168.1.41",
        "192.168.1.42",
        "192.168.1.43",
        "192.168.1.60",
    ]
    miner_net_1 = "192.168.1.0"
    miner_net_1_mask = 29

    #######################
    # Network Range Tests #
    #######################

    net_range_1 = list(MinerNetworkRange(net_range_str).hosts())

    net_range_2 = list(MinerNetworkRange(net_range_list).hosts())

    correct_net_range = [
        ipaddress.IPv4Address("192.168.1.29"),
        ipaddress.IPv4Address("192.168.1.40"),
        ipaddress.IPv4Address("192.168.1.41"),
        ipaddress.IPv4Address("192.168.1.42"),
        ipaddress.IPv4Address("192.168.1.43"),
        ipaddress.IPv4Address("192.168.1.60"),
    ]

    assert net_range_1 == correct_net_range
    assert net_range_2 == correct_net_range

    print("Network Range test succeeded.")

    #######################
    # Miner Network Tests #
    #######################

    miner_net = list(
        MinerNetwork(miner_net_1, mask=miner_net_1_mask).get_network().hosts()
    )

    miner_net_str = list(
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

    assert miner_net == correct_net
    assert miner_net_str == correct_net

    print("Miner Network test succeeded.")


if __name__ == "__main__":
    test_network()
