import asyncio
import ipaddress
import os
import re
import sys
import time
from operator import itemgetter

import PySimpleGUI as sg
import aiofiles
import toml

from miners.miner_factory import MinerFactory
from network import MinerNetwork

icon_of_window = b'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'

layout = [
    [sg.Text('Network IP: '), sg.InputText(key='miner_network', do_not_clear=True, size=(110, 1)),
     sg.Button('Scan', key='scan'),
     sg.Text("", key="status")],
    [sg.Text('IP List File: '), sg.Input(key="file_iplist", do_not_clear=True, size=(110, 1)), sg.FileBrowse(),
     sg.Button('Import', key="import_iplist")],
    [sg.Text('Config File: '), sg.Input(key="file_config", do_not_clear=True, size=(110, 1)), sg.FileBrowse(),
     sg.Button('Import', key="import_file_config"), sg.Button('Export', key="export_file_config")],
    [
        sg.Column([
            [sg.Text("IP List:", pad=(0, 0)), sg.Text("", key="ip_count", pad=(1, 0), size=(3, 1)),
             sg.Button('ALL', key="select_all_ips")],
            [sg.Listbox([], size=(20, 32), key="ip_list", select_mode='extended')]
        ]),
        sg.Column([
            [sg.Text("Data: ", pad=(0, 0)), sg.Button('GET', key="get_data"), sg.Button('SORT IP', key="sort_data_ip"),
             sg.Button('SORT HR', key="sort_data_hr"), sg.Button('SORT USER', key="sort_data_user"), sg.Button('SORT W', key="sort_data_w")],
            [sg.Listbox([], size=(70, 32), key="hr_list")]
        ]),
        sg.Column([
            [sg.Text("Config"), sg.Button("IMPORT", key="import_config"), sg.Button("CONFIG", key="send_config"),
             sg.Button("LIGHT", key="light"), sg.Button("GENERATE", key="generate_config")],
            [sg.Multiline(size=(50, 34), key="config", do_not_clear=True)],
        ])
    ],
]

window = sg.Window('Upstream Config Util', layout, icon=icon_of_window)
miner_factory = MinerFactory()


async def update_ui_with_data(key, data, append=False):
    if append:
        data = window[key].get_text() + data
    window[key].update(data)


async def scan_network(network):
    global window
    await update_ui_with_data("status", "Scanning")
    miners = await network.scan_network_for_miners()
    window["ip_list"].update([str(miner.ip) for miner in miners])
    await update_ui_with_data("ip_count", str(len(miners)))
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
    await update_ui_with_data("config", toml.dumps(config))
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


async def send_config(ips: list, config):
    await update_ui_with_data("status", "Configuring")
    config['format']['generator'] = 'upstream_config_util'
    config['format']['timestamp'] = int(time.time())
    tasks = []
    for ip in ips:
        tasks.append(miner_factory.get_miner(ip))
    miners = await asyncio.gather(*tasks)
    tasks = []
    for miner in miners:
        tasks.append(miner.send_config(config))
    await asyncio.gather(*tasks)
    await update_ui_with_data("status", "")


async def import_config_file(file_location):
    await update_ui_with_data("status", "Importing")
    if not os.path.exists(file_location):
        return
    else:
        async with aiofiles.open(file_location, mode='r') as file:
            config = await file.read()
    await update_ui_with_data("config", str(config))
    await update_ui_with_data("status", "")


async def export_config_file(file_location, config):
    await update_ui_with_data("status", "Exporting")
    config = toml.loads(config)
    config['format']['generator'] = 'upstream_config_util'
    config['format']['timestamp'] = int(time.time())
    config = toml.dumps(config)
    async with aiofiles.open(file_location, mode='w+') as file:
        await file.write(config)
    await update_ui_with_data("status", "")


async def get_data(ip_list: list):
    await update_ui_with_data("status", "Getting Data")
    ips = [ipaddress.ip_address(ip) for ip in ip_list]
    ips.sort()
    data = await asyncio.gather(*[get_formatted_data(miner) for miner in ips])
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
    data = await miner.api.multicommand("summary", "pools", "tunerstatus")
    host = await miner.get_hostname()
    if "tunerstatus" in data.keys():
        wattage = data['tunerstatus'][0]['TUNERSTATUS'][0]['PowerLimit']
    else:
        wattage = 0
    if "summary" in data.keys():
        if 'MHS 5s' in data['summary'][0]['SUMMARY'][0].keys():
            th5s = round(data['summary'][0]['SUMMARY'][0]['MHS 5s'] / 1000000, 2)
        elif 'GHS 5s' in data['summary'][0]['SUMMARY'][0].keys():
            if not data['summary'][0]['SUMMARY'][0]['GHS 5s'] == "":
                th5s = round(float(data['summary'][0]['SUMMARY'][0]['GHS 5s']) / 1000, 2)
            else:
                th5s = 0
        else:
            th5s = 0
    else:
        th5s = 0
    user = data['pools'][0]['POOLS'][0]['User']
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
    window['config'].update(toml.dumps(config))


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


async def ui():
    while True:
        event, value = window.read(timeout=10)
        if event in (None, 'Close'):
            sys.exit()
        if event == 'scan':
            if len(value['miner_network'].split("/")) > 1:
                network = value['miner_network'].split("/")
                miner_network = MinerNetwork(ip_addr=network[0], mask=network[1])
            else:
                miner_network = MinerNetwork(value['miner_network'])
            asyncio.create_task(scan_network(miner_network))
        if event == 'select_all_ips':
            if value['ip_list'] == window['ip_list'].Values:
                window['ip_list'].set_value([])
            else:
                window['ip_list'].set_value(window['ip_list'].Values)
        if event == 'import_config':
            if 2 > len(value['ip_list']) > 0:
                asyncio.create_task(import_config(value['ip_list']))
        if event == 'light':
            asyncio.create_task(miner_light(value['ip_list']))
        if event == "import_iplist":
            asyncio.create_task(import_iplist(value["file_iplist"]))
        if event == "send_config":
            asyncio.create_task(send_config(value['ip_list'], toml.loads(value['config'])))
        if event == "import_file_config":
            asyncio.create_task(import_config_file(value['file_config']))
        if event == "export_file_config":
            asyncio.create_task(export_config_file(value['file_config'], value["config"]))
        if event == "get_data":
            asyncio.create_task(get_data(value['ip_list']))
        if event == "generate_config":
            asyncio.create_task(generate_config())
        if event == "sort_data_ip":
            asyncio.create_task(sort_data('ip'))
        if event == "sort_data_hr":
            asyncio.create_task(sort_data('hr'))
        if event == "sort_data_user":
            asyncio.create_task(sort_data(3))
        if event == "sort_data_w":
            asyncio.create_task(sort_data('wattage'))
        if event == "__TIMEOUT__":
            await asyncio.sleep(0)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ui())
