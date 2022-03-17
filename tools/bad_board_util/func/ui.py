import ipaddress
import re

from tools.bad_board_util.layout import window

import pyperclip


def table_select_all():
    window["ip_table"].update(
        select_rows=(
            [row for row in range(len(window["ip_table"].Values))]
        )
    )


def copy_from_table(table):
    selection = table.selection()
    copy_values = []
    for each in selection:
        try:
            # value = table.item(each)["values"][0]
            table_values = table.item(each)["values"]
            ip = table_values[0]
            model = table_values[1]
            total = str(table_values[2])
            l_brd_chips = str(table_values[3])
            c_brd_chips = str(table_values[5])
            r_brd_chips = str(table_values[7])
            all_values = [ip, model, total, l_brd_chips, c_brd_chips, r_brd_chips]
            value = ", ".join(all_values)

            copy_values.append(str(value))
        except Exception as e:
            print("Copy Error:", e)
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
    # ip addresses
    if re.match("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",
                  str(all_data[0]["data"][index])):
        new_list = sorted(all_data, key=lambda x: ipaddress.ip_address(x["data"][index]))
        if all_data == new_list:
            new_list = sorted(all_data, reverse=True, key=lambda x: ipaddress.ip_address(x["data"][index]))

    # everything else, model, chips
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
