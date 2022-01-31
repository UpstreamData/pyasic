import ipaddress
import os
import re
import time

import aiofiles
import toml

from tools.cfg_util.cfg_util_sg.func.ui import update_ui_with_data
from tools.cfg_util.cfg_util_sg.layout import window
from config.bos import bos_config_convert, general_config_convert_bos


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
    config = await general_config_convert_bos(config)
    config = toml.loads(config)
    config['format']['generator'] = 'upstream_config_util'
    config['format']['timestamp'] = int(time.time())
    config = toml.dumps(config)
    async with aiofiles.open(file_location, mode='w+') as file:
        await file.write(config)
    await update_ui_with_data("status", "")
