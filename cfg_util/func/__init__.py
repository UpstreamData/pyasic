import asyncio
import ipaddress
import os
import re
import time

import aiofiles
import toml

from API import APIError
from cfg_util.func.data import safe_parse_api_data
from cfg_util.layout import window
from cfg_util.miner_factory import miner_factory
from config.bos import bos_config_convert, general_config_convert_bos
from settings import CFG_UTIL_CONFIG_THREADS as CONFIG_THREADS


async def update_ui_with_data(key, message, append=False):
    if append:
        message = window[key].get_text() + message
    window[key].update(message)


async def update_prog_bar(amount):
    window["progress"].Update(amount)
    percent_done = 100 * (amount / window['progress'].maxlen)
    window["progress_percent"].Update(f"{round(percent_done, 2)} %")
    if percent_done == 100:
        window["progress_percent"].Update("")


async def set_progress_bar_len(amount):
    window["progress"].Update(0, max=amount)
    window["progress"].maxlen = amount
    window["progress_percent"].Update("0.0 %")


async def scan_network(network):
    await update_ui_with_data("status", "Scanning")
    network_size = len(network)
    miner_generator = network.scan_network_generator()
    await set_progress_bar_len(2 * network_size)
    progress_bar_len = 0
    miners = []
    async for miner in miner_generator:
        if miner:
            miners.append(miner)
            # can output "Identifying" for each found item, but it gets a bit cluttered
            # and could possibly be confusing for the end user because of timing on
            # adding the IPs
            # window["ip_table"].update([["Identifying...", "", "", "", ""] for miner in miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    progress_bar_len += network_size - len(miners)
    asyncio.create_task(update_prog_bar(progress_bar_len))
    get_miner_genenerator = miner_factory.get_miner_generator(miners)
    all_miners = []
    async for found_miner in get_miner_genenerator:
        all_miners.append(found_miner)
        all_miners.sort(key=lambda x: x.ip)
        window["ip_table"].update([[str(miner.ip), "", "", "", ""] for miner in all_miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("ip_count", str(len(all_miners)))
    await update_ui_with_data("status", "")


async def miner_light(ips: list):
    await asyncio.gather(*[flip_light(ip) for ip in ips])


async def flip_light(ip):
    ip_list = window['ip_table'].Widget
    miner = await miner_factory.get_miner(ip)
    index = [item[0] for item in window["ip_table"].Values].index(ip)
    index_tags = ip_list.item(index)['tags']
    if "light" not in index_tags:
        ip_list.item(index, tags=([*index_tags, "light"]))
        window['ip_table'].update(row_colors=[(index, "white", "red")])
        await miner.fault_light_on()
    else:
        index_tags.remove("light")
        ip_list.item(index, tags=index_tags)
        window['ip_table'].update(row_colors=[(index, "black", "white")])
        await miner.fault_light_off()


async def import_config(idx):
    await update_ui_with_data("status", "Importing")
    miner = await miner_factory.get_miner(ipaddress.ip_address(window["ip_table"].Values[idx[0]][0]))
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
    window["ip_table"].update([[str(ip), "", "", "", ""] for ip in ip_list])
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
                for item in window['ip_table'].Values:
                    await file.write(str(item[0]) + "\n")
    await update_ui_with_data("status", "")


async def send_config_generator(miners: list, config):
    loop = asyncio.get_event_loop()
    config_tasks = []
    for miner in miners:
        if len(config_tasks) >= CONFIG_THREADS:
            configured = asyncio.as_completed(config_tasks)
            config_tasks = []
            for sent_config in configured:
                yield await sent_config
        config_tasks.append(loop.create_task(miner.send_config(config)))
    configured = asyncio.as_completed(config_tasks)
    for sent_config in configured:
        yield await sent_config


async def send_config(ips: list, config):
    await update_ui_with_data("status", "Configuring")
    await set_progress_bar_len(2 * len(ips))
    progress_bar_len = 0
    get_miner_genenerator = miner_factory.get_miner_generator(ips)
    all_miners = []
    async for miner in get_miner_genenerator:
        all_miners.append(miner)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    config_sender_generator = send_config_generator(all_miners, config)
    async for _config_sender in config_sender_generator:
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
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
    if len(ips) == 0:
        ips = [ipaddress.ip_address(ip) for ip in [item[0] for item in window["ip_table"].Values]]
    await set_progress_bar_len(len(ips))
    progress_bar_len = 0
    data_gen = asyncio.as_completed([get_formatted_data(miner) for miner in ips])
    ip_table_data = window["ip_table"].Values
    ordered_all_ips = [item[0] for item in ip_table_data]
    miner_hr = []
    for all_data in data_gen:
        data_point = await all_data
        miner_hr.append(data_point["TH/s"])
        if data_point["IP"] in ordered_all_ips:
            ip_table_index = ordered_all_ips.index(data_point["IP"])
            ip_table_data[ip_table_index] = [
                data_point["IP"], data_point["host"], str(data_point['TH/s']) + " TH/s", data_point['user'], str(data_point['wattage']) + " W"
            ]
            window["ip_table"].update(ip_table_data)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    total_hr = round(sum(miner_hr), 2)
    window["hr_total"].update(f"{total_hr} TH/s")

    await update_ui_with_data("status", "")


async def get_formatted_data(ip: ipaddress.ip_address):
    miner = await miner_factory.get_miner(ip)
    try:
        miner_data = await miner.api.multicommand("summary", "pools", "tunerstatus")
    except APIError:
        return {'TH/s': "Unknown", 'IP': str(miner.ip), 'host': "Unknown", 'user': "Unknown", 'wattage': 0}
    host = await miner.get_hostname()
    if "tunerstatus" in miner_data.keys():
        wattage = await safe_parse_api_data(miner_data, "tunerstatus", 0, 'TUNERSTATUS', 0, "PowerLimit")
        # data['tunerstatus'][0]['TUNERSTATUS'][0]['PowerLimit']
    else:
        wattage = 0
    if "summary" in miner_data.keys():
        if 'MHS 5s' in miner_data['summary'][0]['SUMMARY'][0].keys():
            th5s = round(await safe_parse_api_data(miner_data, 'summary', 0, 'SUMMARY', 0, 'MHS 5s') / 1000000, 2)
        elif 'GHS 5s' in miner_data['summary'][0]['SUMMARY'][0].keys():
            if not miner_data['summary'][0]['SUMMARY'][0]['GHS 5s'] == "":
                th5s = round(float(await safe_parse_api_data(miner_data, 'summary', 0, 'SUMMARY', 0, 'GHS 5s')) / 1000,
                             2)
            else:
                th5s = 0
        else:
            th5s = 0
    else:
        th5s = 0
    if "pools" not in miner_data.keys():
        user = "?"
    elif not miner_data['pools'][0]['POOLS'] == []:
        user = await safe_parse_api_data(miner_data, 'pools', 0, 'POOLS', 0, 'User')
    else:
        user = "Blank"
    return {'TH/s': th5s, 'IP': str(miner.ip), 'host': host, 'user': user, 'wattage': wattage}


async def generate_config(username, workername, v2_allowed):
    if username and workername:
        user = f"{username}.{workername}"
    elif username and not workername:
        user = username
    else:
        return

    if v2_allowed:
        url_1 = 'stratum2+tcp://v2.us-east.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt'
        url_2 = 'stratum2+tcp://v2.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt'
        url_3 = 'stratum+tcp://stratum.slushpool.com:3333'
    else:
        url_1 = 'stratum+tcp://ca.stratum.slushpool.com:3333'
        url_2 = 'stratum+tcp://us-east.stratum.slushpool.com:3333'
        url_3 = 'stratum+tcp://stratum.slushpool.com:3333'

    config = {'group': [{
        'name': 'group',
        'quota': 1,
        'pool': [{
            'url': url_1,
            'user': user,
            'password': '123'
        }, {
            'url': url_2,
            'user': user,
            'password': '123'
        }, {
            'url': url_3,
            'user': user,
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
    data_list = window['ip_table'].Values

    # wattage
    if re.match("[0-9]* W", data_list[0][index]):
        new_list = sorted(data_list, key=lambda x: int(x[index].replace(" W", "")))

    # hashrate
    elif re.match("[0-9]*\.?[0-9]* TH\/s", data_list[0][index]):
        new_list = sorted(data_list, key=lambda x: float(x[index].replace(" TH/s", "")))

    # ip addresses
    elif re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
                  data_list[0][index]):
        new_list = sorted(data_list, key=lambda x: ipaddress.ip_address(x[index]))

    # everything else, hostname and user
    else:
        new_list = sorted(data_list, key=lambda x: x[index])
    await update_ui_with_data("ip_table", new_list)
    await update_ui_with_data("status", "")
