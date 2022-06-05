import asyncio
import ipaddress
from network import MinerNetwork
from miners.miner_factory import MinerFactory
from network.net_range import MinerNetworkRange
import requests
import warnings

def fxn():
    warnings.warn("deprecated", DeprecationWarning)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fxn()


def ip_for_cust(vlan, ip):
    break_ip = ip.split('.')
    return break_ip[2] == vlan


async def get_miners_from_pfsense(vlan):
    url = "https://fw1.distributedha.sh/api/v1/services/dhcpd/lease"
    headers = {'content-type': 'application/json',
               'accept': 'application/json', 
               'Accept-Charset': 'UTF-8',
               'Authorization': 'Basic YXBpX3VzZXI6SE9QTElURSEhZ3JvdXNlODEz'}
    r = requests.get(url, headers=headers)
    data = r.json()
    #print(data['data'])

    macs = {}
    for x in data['data']:
        # limit to only whatsminers for now
        if x['hostname'] != "WhatsMiner": continue
        macs[x['ip']] = x['mac'].replace(':','').upper()

    #miners = list(macs.keys())
    #miners = ["10.10.10.11", "10.10.10.12", "10.10.10.13"]
    #return miners
    print(macs)
    return macs

async def get_power():
    theminers = await get_miners_from_pfsense('10')
    # Miner Network class allows for easy scanning of a network
    #miner_network = MinerNetwork('10.10.10.10-10.10.10.255')
    #miner_network = MinerNetwork('10.10.10.10-10.10.10.175')
    miner_network = MinerNetwork('10.10.30.10-10.10.30.20')
    #miner_network = MinerNetwork(list(theminers.keys()))
    # Miner Network scan function returns Miner classes for all miners found
    miners = await miner_network.scan_network_for_miners()
    # Each miner will return with its own set of functions, and an API class instance
    tasks = [miner.api.summary() for miner in miners]
    # Gather all tasks asynchronously and run them
    pre_data = await asyncio.gather(*tasks)
    parse_tasks = []
    for item in pre_data:
        # safe_parse_api_data parses the data from a miner API
        # It will raise an APIError (from API import APIError) if there is a problem
        parse_tasks.append(item['SUMMARY'][0]['Power'])
    # Gather all tasks asynchronously and run them
    #data = await asyncio.gather(*parse_tasks)
    data = parse_tasks
    # Print a list of all the power
    #print(data)
    power_list = []
    totalpwr = 0
    for x in data:
        power_list.append(x)
        totalpwr += x
    power_list.sort(reverse = True)
    print(power_list)
    print("Total Power: ", totalpwr / 1000, " kW | Average Power: ", totalpwr / len(data))



if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(get_power())
