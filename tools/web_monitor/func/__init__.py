import os
import ipaddress


def get_current_miner_list():
    cur_miners = []
    if os.path.exists(os.path.join(os.getcwd(), "miner_list.txt")):
        with open(os.path.join(os.getcwd(), "miner_list.txt")) as file:
            for line in file.readlines():
                cur_miners.append(line.strip())
    cur_miners = sorted(cur_miners, key=lambda x: ipaddress.ip_address(x))
    return cur_miners
