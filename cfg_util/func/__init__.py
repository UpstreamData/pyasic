import ipaddress
import os
import re
import time
from operator import itemgetter
import asyncio

import aiofiles
import toml

from cfg_util.miner_factory import miner_factory
from cfg_util.layout import window
from cfg_util.func.data import safe_parse_api_data

from config.bos import bos_config_convert, general_config_convert_bos

from API import APIError

from settings import CFG_UTIL_CONFIG_THREADS as CONFIG_THREADS

async def update_ui_with_data(key, data, append=False):
    if append:
        data = window[key].get_text() + data
    window[key].update(data)

async def update_prog_bar(amount):
    window["progress"].Update(amount)


async def scan_network(network):
    await update_ui_with_data("status", "Scanning")
    network_size = len(network)
    miner_generator = network.scan_network_generator()
    window["progress"].Update(0, max=2*network_size)
    progress_bar_len = 0
    miners = []
    async for miner in miner_generator:
        if miner:
            miners.append(miner)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    progress_bar_len += network_size-len(miners)
    asyncio.create_task(update_prog_bar(progress_bar_len))
    get_miner_genenerator = miner_factory.get_miner_generator(miners)
    all_miners = []
    async for found_miner in get_miner_genenerator:
        all_miners.append(found_miner)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    all_miners.sort(key=lambda x: x.ip)
    window["ip_list"].update([str(miner.ip) for miner in all_miners])
    await update_ui_with_data("ip_count", str(len(all_miners)))
    await update_ui_with_data("status", "")


async def miner_light(ips: list):
    await asyncio.gather(*[flip_light(ip) for ip in ips])


async def flip_light(ip):
    listbox = window['ip_list'].Widget
    miner = await miner_factory.get_miner(ip)
    if ip in window["ip_list"].Values:
        index = window["ip_list"].Values.index(ip)
        if listbox.itemcget(index, "background") == 'red':
            listbox.itemconfigure(index, bg='#f0f3f7', fg='#000000')
            await miner.fault_light_off()
        else:
            listbox.itemconfigure(index, bg='red', fg='white')
            await miner.fault_light_on()


async def import_config(ip):
    await update_ui_with_data("status", "Importing")
    miner = await miner_factory.get_miner(ipaddress.ip_address(*ip))
    await miner.get_config()
    config = miner.config
    await update_ui_with_data("config", str(config))
    await update_ui_with_data("status", "")


async def import_iplist(file_location):
    await update_ui_with_data("status", "Importing")
    if not os.path.exists(file_location):
        return
    else:
        ip_list = []
        async with aiofiles.open(file_location, mode='r') as file:
            async for line in file:
                ips = [x.group() for x in re.finditer(
                    "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", line)]
                for ip in ips:
                    if ip not in ip_list:
                        ip_list.append(ipaddress.ip_address(ip))
    ip_list.sort()
    window["ip_list"].update([str(ip) for ip in ip_list])
    await update_ui_with_data("ip_count", str(len(ip_list)))
    await update_ui_with_data("status", "")


async def export_iplist(file_location, ip_list_selected):
    await update_ui_with_data("status", "Exporting")
    if not os.path.exists(file_location):
        return
    else:
        if ip_list_selected is not None and not ip_list_selected == []:
            async with aiofiles.open(file_location, mode='w') as file:
                for item in ip_list_selected:
                    await file.write(str(item) + "\n")
        else:
            async with aiofiles.open(file_location, mode='w') as file:
                for item in window['ip_list'].Values:
                    await file.write(str(item) + "\n")
    await update_ui_with_data("status", "")


async def send_config(ips: list, config):
    await update_ui_with_data("status", "Configuring")
    tasks = []
    for ip in ips:
        tasks.append(miner_factory.get_miner(ip))
    miners = await asyncio.gather(*tasks)
    config_tasks = []
    for miner in miners:
        if len(config_tasks) < CONFIG_THREADS:
            config_tasks.append(miner.send_config(config))
        else:
            await asyncio.gather(*config_tasks)
            config_tasks = []
    await asyncio.gather(*config_tasks)
    await update_ui_with_data("status", "")


async def import_config_file(file_location):
    await update_ui_with_data("status", "Importing")
    if not os.path.exists(file_location):
        return
    else:
        async with aiofiles.open(file_location, mode='r') as file:
            config = await file.read()
    await update_ui_with_data("config", await bos_config_convert(toml.loads(config)))
    await update_ui_with_data("status", "")


async def export_config_file(file_location, config):
    await update_ui_with_data("status", "Exporting")
    config = toml.loads(config)
    config['format']['generator'] = 'upstream_config_util'
    config['format']['timestamp'] = int(time.time())
    config = toml.dumps(config)
    async with aiofiles.open(file_location, mode='w+') as file:
        await file.write(await general_config_convert_bos(config))
    await update_ui_with_data("status", "")


async def get_data(ip_list: list):
    await update_ui_with_data("status", "Getting Data")
    ips = [ipaddress.ip_address(ip) for ip in ip_list]
    window["progress"].Update(0, max=len(ips))
    progress_bar_len = 0
    data_gen = asyncio.as_completed([get_formatted_data(miner) for miner in ips])
    data = []
    for all_data in data_gen:
        data.append(await all_data)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    data.sort(key=lambda x: ipaddress.ip_address(x['IP']))

    total_hr = round(sum(d.get('TH/s', 0) for d in data), 2)
    window["hr_total"].update(f"{total_hr} TH/s")
    window["hr_list"].update(disabled=False)
    window["hr_list"].update([item['IP'] + " | "
                              + item['host'] + " | "
                              + str(item['TH/s']) + " TH/s | "
                              + item['user'] + " | "
                              + str(item['wattage']) + " W"
                              for item in data])
    window["hr_list"].update(disabled=True)
    await update_ui_with_data("status", "")


async def get_formatted_data(ip: ipaddress.ip_address):
    miner = await miner_factory.get_miner(ip)
    try:
        data = await miner.api.multicommand("summary", "pools", "tunerstatus")
    except APIError:
        return {'TH/s': "Unknown", 'IP': str(miner.ip), 'host': "Unknown", 'user': "Unknown", 'wattage': 0}
    host = await miner.get_hostname()
    if "tunerstatus" in data.keys():
        wattage = await safe_parse_api_data(data, "tunerstatus", 0, 'TUNERSTATUS', 0, "PowerLimit")
        # data['tunerstatus'][0]['TUNERSTATUS'][0]['PowerLimit']
    else:
        wattage = 0
    if "summary" in data.keys():
        if 'MHS 5s' in data['summary'][0]['SUMMARY'][0].keys():
            th5s = round(await safe_parse_api_data(data, 'summary', 0, 'SUMMARY', 0, 'MHS 5s') / 1000000, 2)
        elif 'GHS 5s' in data['summary'][0]['SUMMARY'][0].keys():
            if not data['summary'][0]['SUMMARY'][0]['GHS 5s'] == "":
                th5s = round(float(await safe_parse_api_data(data, 'summary', 0, 'SUMMARY', 0, 'GHS 5s')) / 1000, 2)
            else:
                th5s = 0
        else:
            th5s = 0
    else:
        th5s = 0
    if "pools" not in data.keys():
        user = "?"
    elif not data['pools'][0]['POOLS'] == []:
        user = await safe_parse_api_data(data, 'pools', 0, 'POOLS', 0, 'User')
    else:
        user = "Blank"
    return {'TH/s': th5s, 'IP': str(miner.ip), 'host': host, 'user': user, 'wattage': wattage}


async def generate_config():
    config = {'group': [{
        'name': 'group',
        'quota': 1,
        'pool': [{
            'url': 'stratum2+tcp://us-east.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt',
            'user': 'UpstreamDataInc.test',
            'password': '123'
        }, {
            'url': 'stratum2+tcp://stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt',
            'user': 'UpstreamDataInc.test',
            'password': '123'
        }, {
            'url': 'stratum+tcp://stratum.slushpool.com:3333',
            'user': 'UpstreamDataInc.test',
            'password': '123'
        }]
    }],
        'format': {
            'version': '1.2+',
            'model': 'Antminer S9',
            'generator': 'upstream_config_util',
            'timestamp': int(time.time())
        },
        'temp_control': {
            'target_temp': 80.0,
            'hot_temp': 90.0,
            'dangerous_temp': 120.0
        },
        'autotuning': {
            'enabled': True,
            'psu_power_limit': 900
        }
    }
    window['config'].update(await bos_config_convert(config))


async def sort_data(index: int or str):
    await update_ui_with_data("status", "Sorting Data")
    data_list = window['hr_list'].Values
    new_list = []
    indexes = {}
    for item in data_list:
        item_data = [part.strip() for part in item.split("|")]
        for idx, part in enumerate(item_data):
            if re.match("[0-9]* W", part):
                item_data[idx] = item_data[idx].replace(" W", "")
                indexes['wattage'] = idx
            elif re.match("[0-9]*\.?[0-9]* TH\/s", part):
                item_data[idx] = item_data[idx].replace(" TH/s", "")
                indexes['hr'] = idx
            elif re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", part):
                item_data[idx] = ipaddress.ip_address(item_data[idx])
                indexes['ip'] = idx
        new_list.append(item_data)
    if not isinstance(index, str):
        if index == indexes['hr']:
            new_data_list = sorted(new_list, key=lambda x: float(x[index]))
        else:
            new_data_list = sorted(new_list, key=itemgetter(index))
    else:
        if index.lower() not in indexes.keys():
            return
        elif index.lower() == 'hr':
            new_data_list = sorted(new_list, key=lambda x: float(x[indexes[index]]))
        else:
            new_data_list = sorted(new_list, key=itemgetter(indexes[index]))
    new_ip_list = []
    for item in new_data_list:
        new_ip_list.append(item[indexes['ip']])
    new_data_list = [str(item[indexes['ip']]) + " | "
                     + item[1] + " | "
                     + item[indexes['hr']] + " TH/s | "
                     + item[3] + " | "
                     + str(item[indexes['wattage']]) + " W"
                     for item in new_data_list]
    window["hr_list"].update(disabled=False)
    window["hr_list"].update(new_data_list)
    window['ip_list'].update(new_ip_list)
    window["hr_list"].update(disabled=True)
    await update_ui_with_data("status", "")
