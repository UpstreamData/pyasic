import asyncio
import ipaddress
import os
import re
import sys
import time

import PySimpleGUI as sg
import aiofiles
import toml

from miners.miner_factory import MinerFactory
from network import MinerNetwork

layout = [
    [sg.Text('Network IP: '), sg.InputText(key='miner_network', do_not_clear=True, size=(70, 1)),
     sg.Button('Scan', key='scan'),
     sg.Text("", key="status")],
    [sg.Text('IP List File: '), sg.Input(key="file_iplist", do_not_clear=True, size=(70, 1)), sg.FileBrowse(),
     sg.Button('Import', key="import_iplist")],
    [sg.Text('Config File: '), sg.Input(key="file_config", do_not_clear=True, size=(70, 1)), sg.FileBrowse(),
     sg.Button('Import', key="import_file_config"), sg.Button('Export', key="export_file_config")],
    [
        sg.Column([
            [sg.Text("IP List:", pad=(0, 0)), sg.Text("", key="ip_count", pad=(1, 0), size=(3, 1)),
             sg.Button('ALL', key="select_all_ips")],
            [sg.Listbox([], size=(20, 32), key="ip_list", select_mode='extended')]
        ]),
        sg.Column([
            [sg.Text("Hashrates: ", pad=(0, 0)), sg.Button('GET', key="get_hashrates")],
            [sg.Listbox([], size=(25, 32), key="hr_list")]
        ]),
        sg.Column([
            [sg.Text("Config"), sg.Button("IMPORT", key="import_config"), sg.Button("CONFIG", key="send_config"),
             sg.Button("LIGHT", key="light"), sg.Button("GENERATE", key="generate_config")],
            [sg.Multiline(size=(50, 34), key="config", do_not_clear=True)],
        ])
    ],
]

window = sg.Window('Test', layout)
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
    listbox = window['ip_list']
    for ip in ips:
        if ip in window["ip_list"].Values:
            index = window["ip_list"].Values.index(ip)
            if listbox.itemcget(index, "background") == 'red':
                listbox.itemconfigure(index, bg='#f0f3f7', fg='#000000')
            else:
                listbox.itemconfigure(index, bg='red', fg='white')


async def import_config(ip):
    await update_ui_with_data("status", "Importing")
    miner = await miner_factory.get_miner(ipaddress.ip_address(*ip))
    await miner.get_config()
    config = miner.config
    print(config)
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
                ips = [x.group() for x in re.finditer("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)", line)]
                for ip in ips:
                    if ip not in ip_list:
                        ip_list.append(ipaddress.ip_address(ip))
    ip_list.sort()
    window["ip_list"].update([str(ip) for ip in ip_list])
    await update_ui_with_data("ip_count", str(len(ip_list)))
    await update_ui_with_data("status", "")


async def send_config(ips: list, config):
    await update_ui_with_data("status", "Configuring")
    config = toml.loads(config)
    config['format']['generator'] = 'upstream_config_util'
    config['format']['timestamp'] = int(time.time())
    config = toml.dumps(config)
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


async def get_hashrates(ip_list: list):
    await update_ui_with_data("status", "Getting HR")
    ips = [ipaddress.ip_address(ip) for ip in ip_list]
    ips.sort()
    data = await asyncio.gather(*[get_formatted_hashrate(miner) for miner in ips])
    window["hr_list"].update(disabled=False)
    window["hr_list"].update([item['IP'] + " | " + str(item['TH/s']) + " TH/s" for item in data])
    window["hr_list"].update(disabled=True)

    await update_ui_with_data("status", "")


async def get_formatted_hashrate(ip: ipaddress.ip_address):
    miner = await miner_factory.get_miner(ip)
    data = await miner.api.summary()
    mh5s = round(data['SUMMARY'][0]['MHS 5s'] / 1000000, 2)
    return {'TH/s': mh5s, 'IP': str(miner.ip)}


async def generate_config():
    config = {'group': [{'name': 'group', 'quota': 1, 'pool': [{'url': 'stratum2+tcp://us-east.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt', 'user': 'UpstreamDataInc.test', 'password': '123'}, {'url': 'stratum2+tcp://stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt', 'user': 'UpstreamDataInc.test', 'password': '123'}, {'url': 'stratum+tcp://stratum.slushpool.com:3333', 'user': 'UpstreamDataInc.test', 'password': '123'}]}], 'format': {'version': '1.2+', 'model': 'Antminer S9', 'generator': 'upstream_config_util', 'timestamp': int(time.time())}, 'temp_control': {'target_temp': 80.0, 'hot_temp': 90.0, 'dangerous_temp': 120.0}, 'autotuning': {'enabled': True, 'psu_power_limit': 900}}
    window['config'].update(toml.dumps(config))


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
        if event == "get_hashrates":
            asyncio.create_task(get_hashrates(value['ip_list']))
        if event == "generate_config":
            asyncio.create_task(generate_config())
        if event == "__TIMEOUT__":
            await asyncio.sleep(0)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(ui())
