import asyncio
import ipaddress
import time
import warnings
import logging

from API import APIError
from tools.cfg_util.cfg_util_sg.func.parse_data import safe_parse_api_data
from tools.cfg_util.cfg_util_sg.func.ui import update_ui_with_data, update_prog_bar, set_progress_bar_len
from tools.cfg_util.cfg_util_sg.layout import window
from miners.miner_factory import MinerFactory
from config.bos import bos_config_convert
from tools.cfg_util.cfg_util_sg.func.decorators import disable_buttons
from settings import CFG_UTIL_CONFIG_THREADS as CONFIG_THREADS, CFG_UTIL_REBOOT_THREADS as REBOOT_THREADS


async def import_config(idx):
    await update_ui_with_data("status", "Importing")
    logging.debug(f"{window['ip_table'].Values[idx[0]][0]}: Importing config.")
    miner = await MinerFactory().get_miner(ipaddress.ip_address(window["ip_table"].Values[idx[0]][0]))
    await miner.get_config()
    config = miner.config
    await update_ui_with_data("config", str(config))
    logging.debug(f"{window['ip_table'].Values[idx[0]][0]}: Config import completed.")
    await update_ui_with_data("status", "")


@disable_buttons
async def scan_network(network):
    await update_ui_with_data("status", "Scanning")
    await update_ui_with_data("ip_count", "")
    await update_ui_with_data("hr_total", "")
    window["ip_table"].update([])
    network_size = len(network)
    miner_generator = network.scan_network_generator()
    await set_progress_bar_len(2 * network_size)
    progress_bar_len = 0
    asyncio.create_task(update_prog_bar(progress_bar_len))
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
    get_miner_genenerator = MinerFactory().get_miner_generator(miners)
    all_miners = []
    async for found_miner in get_miner_genenerator:
        all_miners.append(found_miner)
        all_miners.sort(key=lambda x: x.ip)
        window["ip_table"].update([[str(miner.ip)] for miner in all_miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("ip_count", str(len(all_miners)))
    await update_ui_with_data("status", "")


@disable_buttons
async def miner_light(ips: list):
    await asyncio.gather(*[flip_light(ip) for ip in ips])


async def flip_light(ip):
    ip_list = window['ip_table'].Widget
    miner = await MinerFactory().get_miner(ip)
    index = [item[0] for item in window["ip_table"].Values].index(ip)
    index_tags = ip_list.item(index + 1)['tags']
    if "light" not in index_tags:
        index_tags.append("light")
        ip_list.item(index + 1, tags=index_tags)
        await miner.fault_light_on()
    else:
        index_tags.remove("light")
        ip_list.item(index + 1, tags=index_tags)
        await miner.fault_light_off()


async def send_command_generator(miners: list, command: str):
    loop = asyncio.get_event_loop()
    command_tasks = []
    for miner in miners:
        if len(command_tasks) >= CONFIG_THREADS:
            cmd_sent = asyncio.as_completed(command_tasks)
            command_tasks = []
            for done in cmd_sent:
                yield await done
        command_tasks.append(loop.create_task(send_ssh_command(miner, command)))
    cmd_sent = asyncio.as_completed(command_tasks)
    for done in cmd_sent:
        yield await done


async def send_ssh_command(miner, command: str):
    proc = await miner.send_ssh_command(command)
    return {"IP": miner.ip, "proc": proc}


async def send_miners_ssh_commands(ips: list, command: str, ssh_cmd_window):
    get_miner_genenerator = MinerFactory().get_miner_generator(ips)
    all_miners = []
    async for miner in get_miner_genenerator:
        all_miners.append(miner)

    data = []
    send_cmd_generator = send_command_generator(all_miners, command)
    async for command_sent in send_cmd_generator:
        data.append(command_sent)

    proc_table_data = [[ip, ""] for ip in ips]
    for item in data:

        if item["proc"].returncode == 0:
            return_data = item["proc"].stdout
        else:
            return_data = item["proc"].stderr
        if str(item["IP"]) in ips:
            proc_table_index = ips.index(str(item["IP"]))
            proc_table_data[proc_table_index] = [
                str(item["IP"]), return_data.replace("\n", " "),
            ]
            ssh_cmd_window["ssh_cmd_table"].update(proc_table_data)


async def reboot_generator(miners: list):
    loop = asyncio.get_event_loop()
    reboot_tasks = []
    for miner in miners:
        if len(reboot_tasks) >= REBOOT_THREADS:
            rebooted = asyncio.as_completed(reboot_tasks)
            reboot_tasks = []
            for done in rebooted:
                yield await done
        reboot_tasks.append(loop.create_task(miner.reboot()))
    rebooted = asyncio.as_completed(reboot_tasks)
    for done in rebooted:
        yield await done


@disable_buttons
async def reboot_miners(ips: list):
    await update_ui_with_data("status", "Rebooting")
    await set_progress_bar_len(2 * len(ips))
    progress_bar_len = 0
    get_miner_genenerator = MinerFactory().get_miner_generator(ips)
    all_miners = []
    async for miner in get_miner_genenerator:
        all_miners.append(miner)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    reboot_miners_generator = reboot_generator(all_miners)
    async for _rebooter in reboot_miners_generator:
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("status", "")


async def restart_backend_generator(miners: list):
    loop = asyncio.get_event_loop()
    reboot_tasks = []
    for miner in miners:
        if len(reboot_tasks) >= REBOOT_THREADS:
            rebooted = asyncio.as_completed(reboot_tasks)
            reboot_tasks = []
            for done in rebooted:
                yield await done
        reboot_tasks.append(loop.create_task(miner.restart_backend()))
    rebooted = asyncio.as_completed(reboot_tasks)
    for done in rebooted:
        yield await done


@disable_buttons
async def restart_miners_backend(ips: list):
    await update_ui_with_data("status", "Restarting Backends")
    await set_progress_bar_len(2 * len(ips))
    progress_bar_len = 0
    get_miner_genenerator = MinerFactory().get_miner_generator(ips)
    all_miners = []
    async for miner in get_miner_genenerator:
        all_miners.append(miner)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    reboot_miners_generator = reboot_generator(all_miners)
    async for _rebooter in reboot_miners_generator:
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
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


@disable_buttons
async def send_config(ips: list, config):
    await update_ui_with_data("status", "Configuring")
    await set_progress_bar_len(2 * len(ips))
    progress_bar_len = 0
    asyncio.create_task(update_prog_bar(progress_bar_len))
    get_miner_genenerator = MinerFactory().get_miner_generator(ips)
    all_miners = []
    async for miner in get_miner_genenerator:
        all_miners.append(miner)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    config_sender_generator = send_config_generator(all_miners, config)
    async for _config_sender in config_sender_generator:
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("status", "Getting Data")
    await asyncio.sleep(3)
    await refresh_data(ips)


@disable_buttons
async def refresh_data(ip_list: list):
    await update_ui_with_data("status", "Getting Data")
    await update_ui_with_data("hr_total", "")
    ips = [ipaddress.ip_address(ip) for ip in ip_list]
    if len(ips) == 0:
        ips = [ipaddress.ip_address(ip) for ip in [item[0] for item in window["ip_table"].Values]]
    await set_progress_bar_len(len(ips))
    progress_bar_len = 0
    asyncio.create_task(update_prog_bar(progress_bar_len))
    reset_table_values = []
    for item in window["ip_table"].Values:
        if item[0] in ip_list:
            reset_table_values.append([item[0]])
        else:
            reset_table_values.append(item)
    window["ip_table"].update(reset_table_values)
    progress_bar_len = 0
    data_gen = asyncio.as_completed([get_formatted_data(miner) for miner in ips])
    ip_table_data = window["ip_table"].Values
    ordered_all_ips = [item[0] for item in ip_table_data]
    for all_data in data_gen:
        data_point = await all_data
        if data_point["IP"] in ordered_all_ips:
            ip_table_index = ordered_all_ips.index(data_point["IP"])
            ip_table_data[ip_table_index] = [
                data_point["IP"], data_point["model"], data_point["host"], str(data_point['TH/s']) + " TH/s ",
                data_point["temp"],
                data_point['user'], str(data_point['wattage']) + " W"
            ]
            window["ip_table"].update(ip_table_data)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    hashrate_list = []
    hr_idx = 3
    for item, _ in enumerate(window["ip_table"].Values):
        if len(window["ip_table"].Values[item]) > hr_idx:
            if not window["ip_table"].Values[item][hr_idx] == '':
                hashrate_list.append(float(window["ip_table"].Values[item][hr_idx].replace(" TH/s ", "")))
            else:
                hashrate_list.append(0)
        else:
            hashrate_list.append(0)

    total_hr = round(sum(hashrate_list), 2)
    window["hr_total"].update(f"{total_hr} TH/s")

    await update_ui_with_data("status", "")


@disable_buttons
async def scan_and_get_data(network):
    await update_ui_with_data("status", "Scanning")
    await update_ui_with_data("hr_total", "")
    await update_ui_with_data("ip_count", "")
    await update_ui_with_data("ip_table", [])
    network_size = len(network)
    miner_generator = network.scan_network_generator()
    MinerFactory().clear_cached_miners()

    logging.info(f"Scanning network: {str(network)}")

    await set_progress_bar_len(3 * network_size)
    progress_bar_len = 0
    miners = []
    async for miner in miner_generator:
        if miner:
            miners.append(miner)
            # can output "Identifying" for each found item, but it gets a bit cluttered
            # and could possibly be confusing for the end user because of timing on
            # adding the IPs
            # window["ip_table"].update([["Identifying..."] for miner in miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    logging.info(f"Found {len(miners)} Miners")
    logging.debug(f"Found miners: {miners}")
    progress_bar_len += network_size - len(miners)
    asyncio.create_task(update_prog_bar(progress_bar_len))
    get_miner_genenerator = MinerFactory().get_miner_generator(miners)
    all_miners = []
    async for found_miner in get_miner_genenerator:
        all_miners.append(found_miner)
        all_miners.sort(key=lambda x: x.ip)
        window["ip_table"].update([[str(miner.ip)] for miner in all_miners])
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    logging.info(f"Resolved {len(all_miners)} Miners")
    logging.debug(f"Resolved to miner types: {all_miners}")
    await update_ui_with_data("ip_count", str(len(all_miners)))
    data_gen = asyncio.as_completed([get_formatted_data(miner) for miner in miners])
    ip_table_data = window["ip_table"].Values
    ordered_all_ips = [item[0] for item in ip_table_data]
    progress_bar_len += (network_size - len(miners))
    asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("status", "Getting Data")
    logging.debug("Getting data on miners.")
    for all_data in data_gen:
        data_point = await all_data
        if data_point["IP"] in ordered_all_ips:
            ip_table_index = ordered_all_ips.index(data_point["IP"])
            ip_table_data[ip_table_index] = [
                data_point["IP"], data_point["model"], data_point["host"], str(data_point['TH/s']) + " TH/s ",
                data_point["temp"],
                data_point['user'], str(data_point['wattage']) + " W"
            ]
            window["ip_table"].update(ip_table_data)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    hashrate_list = [float(item[3].replace(" TH/s ", "")) for item in window["ip_table"].Values if not item[3] == '']
    total_hr = round(sum(hashrate_list), 2)
    await update_ui_with_data("hr_total", f"{total_hr} TH/s")
    await update_ui_with_data("status", "")


async def get_formatted_data(ip: ipaddress.ip_address):
    miner = await MinerFactory().get_miner(ip)
    logging.debug(f"Getting data for miner: {miner.ip}")
    warnings.filterwarnings('ignore')
    miner_data = None
    host = await miner.get_hostname()
    try:
        model = await miner.get_model()
    except APIError:
        model = "?"
    if not model:
        model = "?"
    temps = 0
    th5s = 0
    wattage = 0
    user = "?"

    try:
        miner_data = await miner.api.multicommand("summary", "devs", "temps", "tunerstatus", "pools", "stats")
    except APIError:
        try:
            # no devs command, it will fail in this case
            miner_data = await miner.api.multicommand("summary", "temps", "tunerstatus", "pools", "stats")
        except APIError as e:
            logging.warning(f"{str(ip)}: {e}")
            return {'TH/s': 0, 'IP': str(miner.ip), 'model': 'Unknown', 'temp': 0, 'host': 'Unknown', 'user': 'Unknown',
                    'wattage': 0}
    if miner_data:
        logging.info(f"Received miner data for miner: {miner.ip}")
        # get all data from summary
        if "summary" in miner_data.keys():
            if not miner_data["summary"][0].get("SUMMARY") == [] and "SUMMARY" in miner_data["summary"][0].keys():
                # temperature data, this is the idea spot to get this
                if "Temperature" in miner_data['summary'][0]['SUMMARY'][0].keys():
                    if not round(miner_data['summary'][0]['SUMMARY'][0]["Temperature"]) == 0:
                        temps = miner_data['summary'][0]['SUMMARY'][0]["Temperature"]
                # hashrate data
                if 'MHS av' in miner_data['summary'][0]['SUMMARY'][0].keys():
                    th5s = format(round(await safe_parse_api_data(miner_data, 'summary', 0, 'SUMMARY', 0, 'MHS av') / 1000000, 2), ".2f").rjust(6, " ")
                elif 'GHS av' in miner_data['summary'][0]['SUMMARY'][0].keys():
                    if not miner_data['summary'][0]['SUMMARY'][0]['GHS av'] == "":
                        th5s = format(round(
                            float(await safe_parse_api_data(miner_data, 'summary', 0, 'SUMMARY', 0, 'GHS av')) / 1000,
                            2), ".2f").rjust(6, " ")

        # alternate temperature data, for BraiinsOS
        if "temps" in miner_data.keys():
            if not miner_data["temps"][0].get('TEMPS') == []:
                if "Chip" in miner_data["temps"][0]['TEMPS'][0].keys():
                    for board in miner_data["temps"][0]['TEMPS']:
                        if board["Chip"] is not None and not board["Chip"] == 0.0:
                            temps = board["Chip"]
        # alternate temperature data, for Whatsminers
        if "devs" in miner_data.keys():
            if not miner_data["devs"][0].get('DEVS') == []:
                if "Chip Temp Avg" in miner_data["devs"][0]['DEVS'][0].keys():
                    for board in miner_data["devs"][0]['DEVS']:
                        if board['Chip Temp Avg'] is not None and not board['Chip Temp Avg'] == 0.0:
                            temps = board['Chip Temp Avg']
        # alternate temperature data
        if "stats" in miner_data.keys():
            if not miner_data["stats"][0]['STATS'] == []:
                for temp in ["temp2", "temp1", "temp3"]:
                    if temp in miner_data["stats"][0]['STATS'][1].keys():
                        if miner_data["stats"][0]['STATS'][1][temp] is not None and not miner_data["stats"][0]['STATS'][1][temp] == 0.0:
                            temps = miner_data["stats"][0]['STATS'][1][temp]
            # alternate temperature data, for Avalonminers
            miner_data["stats"][0]['STATS'][0].keys()
            if any("MM ID" in string for string in miner_data["stats"][0]['STATS'][0].keys()):
                temp_all = []
                for key in [string for string in miner_data["stats"][0]['STATS'][0].keys() if "MM ID" in string]:
                    for value in [string for string in miner_data["stats"][0]['STATS'][0][key].split(" ") if
                                  "TMax" in string]:
                        temp_all.append(int(value.split("[")[1].replace("]", "")))
                temps = round(sum(temp_all) / len(temp_all))

        # pool information
        if "pools" in miner_data.keys():
            if not miner_data['pools'][0].get('POOLS') == []:
                user = await safe_parse_api_data(miner_data, 'pools', 0, 'POOLS', 0, 'User')
            else:
                print(miner_data['pools'][0])
                user = "Blank"

        # braiins tuner status / wattage
        if "tunerstatus" in miner_data.keys():
            wattage = await safe_parse_api_data(miner_data, "tunerstatus", 0, 'TUNERSTATUS', 0, "PowerLimit")
        elif "Power" in miner_data["summary"][0]["SUMMARY"][0].keys():
            wattage = await safe_parse_api_data(miner_data, "summary", 0, 'SUMMARY', 0, "Power")

    ret_data = {'TH/s': th5s, 'IP': str(miner.ip), 'model': model,
            'temp': round(temps), 'host': host, 'user': user,
            'wattage': wattage}

    logging.debug(f"{ret_data}")

    return ret_data


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
