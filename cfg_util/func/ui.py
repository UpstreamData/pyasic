import ipaddress
import re

from cfg_util.layout import window


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


async def sort_data(index: int or str):
    await update_ui_with_data("status", "Sorting Data")
    data_list = window['ip_table'].Values

    # wattage
    if re.match("[0-9]* W", str(data_list[0][index])):
        new_list = sorted(data_list, key=lambda x: int(x[index].replace(" W", "")))
        if data_list == new_list:
            new_list = sorted(data_list, reverse=True, key=lambda x: int(x[index].replace(" W", "")))

    # hashrate
    elif re.match("[0-9]*\.?[0-9]* TH\/s", str(data_list[0][index])):
        new_list = sorted(data_list, key=lambda x: float(x[index].replace(" TH/s", "")))
        if data_list == new_list:
            new_list = sorted(data_list, reverse=True, key=lambda x: float(x[index].replace(" TH/s", "")))

    # ip addresses
    elif re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
                  str(data_list[0][index])):
        new_list = sorted(data_list, key=lambda x: ipaddress.ip_address(x[index]))
        if data_list == new_list:
            new_list = sorted(data_list, reverse=True, key=lambda x: ipaddress.ip_address(x[index]))

    # everything else, hostname, temp, and user
    else:
        new_list = sorted(data_list, key=lambda x: x[index])
        if data_list == new_list:
            new_list = sorted(data_list, reverse=True, key=lambda x: x[index])

    await update_ui_with_data("ip_table", new_list)
    await update_ui_with_data("status", "")
