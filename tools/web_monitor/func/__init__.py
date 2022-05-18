import os
import ipaddress

dir_path = "\\".join(os.path.dirname(os.path.realpath(__file__)).split("\\")[:-1])


def get_current_miner_list():
    cur_miners = []
    if os.path.exists(os.path.join(dir_path, "miner_list.txt")):
        with open(os.path.join(dir_path, "miner_list.txt")) as file:
            for line in file.readlines():
                cur_miners.append(line.strip())
    cur_miners = sorted(cur_miners, key=lambda x: ipaddress.ip_address(x))
    return cur_miners
