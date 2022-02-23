import ipaddress
import re

from tools.cfg_util.cfg_util_sg.layout import window

import pyperclip


def copy_from_table(table):
    selection = table.selection()
    copy_values = []
    for each in selection:
        try:
            value = table.item(each)["values"][0]
            copy_values.append(str(value))
        except:
            pass
    copy_string = "\n".join(copy_values)
    pyperclip.copy(copy_string)


def copy_from_ssh_table(table):
    selection = table.selection()
    copy_values = []
    for each in selection:
        try:
            value = ", ".join(table.item(each)["values"])
            copy_values.append(str(value))
        except:
            pass
    copy_string = "\n".join(copy_values)
    pyperclip.copy(copy_string)



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
    if window["scan"].Disabled:
        return
    await update_ui_with_data("status", "Sorting Data")
    data_list = window['ip_table'].Values
    table = window["ip_table"].Widget
    all_data = []
    for idx, item in enumerate(data_list):
        all_data.append({"data": item, "tags": table.item(int(idx) + 1)["tags"]})

    # wattage
    if re.match("[0-9]* W", str(all_data[0]["data"][index])):
        new_list = sorted(all_data, key=lambda x: int(x["data"][index].replace(" W", "")))
        if all_data == new_list:
            new_list = sorted(all_data, reverse=True, key=lambda x: int(x["data"][index].replace(" W", "")))

    # hashrate
    elif re.match("[0-9]*\.?[0-9]* TH\/s", str(all_data[0]["data"][index])):
        new_list = sorted(all_data, key=lambda x: float(x["data"][index].replace(" TH/s", "")))
        if all_data == new_list:
            new_list = sorted(all_data, reverse=True, key=lambda x: float(x["data"][index].replace(" TH/s", "")))

    # ip addresses
    elif re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
                  str(all_data[0]["data"][index])):
        new_list = sorted(all_data, key=lambda x: ipaddress.ip_address(x["data"][index]))
        if all_data == new_list:
            new_list = sorted(all_data, reverse=True, key=lambda x: ipaddress.ip_address(x["data"][index]))

    # everything else, hostname, temp, and user
    else:
        new_list = sorted(all_data, key=lambda x: x["data"][index])
        if all_data == new_list:
            new_list = sorted(all_data, reverse=True, key=lambda x: x["data"][index])

    new_data = []
    for item in new_list:
        new_data.append(item["data"])

    await update_ui_with_data("ip_table", new_data)
    for idx, item in enumerate(new_list):
        table.item(idx + 1, tags=item["tags"])

    await update_ui_with_data("status", "")
