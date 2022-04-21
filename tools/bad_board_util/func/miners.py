import asyncio
import ipaddress
import warnings

from tools.bad_board_util.func.ui import (
    update_ui_with_data,
    update_prog_bar,
    set_progress_bar_len,
)
from tools.bad_board_util.layout import window
from miners.miner_factory import MinerFactory
from tools.bad_board_util.func.decorators import disable_buttons


@disable_buttons
async def scan_network(network):
    await update_ui_with_data("status", "Scanning")
    await update_ui_with_data("ip_count", "")
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
async def refresh_data(ip_list: list):
    await update_ui_with_data("status", "Getting Data")
    ips = [ipaddress.ip_address(ip) for ip in ip_list]
    if len(ips) == 0:
        ips = [
            ipaddress.ip_address(ip)
            for ip in [item[0] for item in window["ip_table"].Values]
        ]
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
    row_colors = []
    for all_data in data_gen:
        data_point = await all_data
        if data_point["IP"] in ordered_all_ips:
            ip_table_index = ordered_all_ips.index(data_point["IP"])
            board_left = ""
            board_center = ""
            board_right = ""
            if data_point["data"]:
                if 0 in data_point["data"].keys():
                    board_left = " ".join(
                        [chain["chip_status"] for chain in data_point["data"][0]]
                    ).replace("o", "•")
                else:
                    row_colors.append((ip_table_index, "white", "red"))
                if 1 in data_point["data"].keys():
                    board_center = " ".join(
                        [chain["chip_status"] for chain in data_point["data"][1]]
                    ).replace("o", "•")
                else:
                    row_colors.append((ip_table_index, "white", "red"))
                if 2 in data_point["data"].keys():
                    board_right = " ".join(
                        [chain["chip_status"] for chain in data_point["data"][2]]
                    ).replace("o", "•")
                else:
                    row_colors.append((ip_table_index, "white", "red"))
                if False in [
                    chain["nominal"]
                    for chain in [
                        data_point["data"][key] for key in data_point["data"].keys()
                    ][0]
                ]:
                    row_colors.append((ip_table_index, "white", "red"))
            else:
                row_colors.append((ip_table_index, "white", "red"))

            data = [
                data_point["IP"],
                data_point["model"],
                len(board_left),
                board_left,
                len(board_center),
                board_center,
                len(board_right),
                board_right,
            ]
            ip_table_data[ip_table_index] = data
            window["ip_table"].update(ip_table_data, row_colors=row_colors)
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))
    await update_ui_with_data("status", "")


@disable_buttons
async def scan_and_get_data(network):
    # update status and reset the table
    await update_ui_with_data("status", "Scanning")
    await update_ui_with_data("ip_count", "")
    await update_ui_with_data("ip_table", [])

    # set progress bar length to network size
    network_size = len(network)
    await set_progress_bar_len(3 * network_size)
    progress_bar_len = 0

    miners = []

    # scan the network for miners using a generator
    async for miner in network.scan_network_generator():
        # the generator will either return None or an IP address
        if miner:
            miners.append(miner)

        # add to the progress bar length after scanning an address
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    # add progress for the miners that we aren't going to identify
    progress_bar_len += network_size - len(miners)
    asyncio.create_task(update_prog_bar(progress_bar_len))

    all_miners = []

    # identify different miner instances using the miner factory generator
    async for found_miner in MinerFactory().get_miner_generator(miners):
        # miner factory generator will always return a miner
        all_miners.append(found_miner)

        # sort the list of miners by IP address
        all_miners.sort(key=lambda x: x.ip)

        # add the new miner to the table
        window["ip_table"].update([[str(miner.ip)] for miner in all_miners])

        # update progress bar
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    # update the count of found miners
    await update_ui_with_data("ip_count", str(len(all_miners)))

    # update progress bar for miners we wont get data for
    progress_bar_len += network_size - len(miners)
    asyncio.create_task(update_prog_bar(progress_bar_len))

    # get the list of IP addresses from the table
    ip_table_data = window["ip_table"].Values
    ordered_all_ips = [item[0] for item in ip_table_data]

    await update_ui_with_data("status", "Getting Data")
    row_colors = []

    # create an in place generator for getting data
    for all_data in asyncio.as_completed(
        [get_formatted_data(miner) for miner in miners]
    ):
        # wait for a generator item to return
        data_point = await all_data

        # make sure the IP is one we have
        # this will likely never fail, but a good failsafe
        if data_point["IP"] in ordered_all_ips:
            # get the index of the IP in the table
            ip_table_index = ordered_all_ips.index(data_point["IP"])

            board_left = ""
            board_center = ""
            board_right = ""

            # make sure we have data, some miners don't allow getting board data
            if data_point["data"]:

                # check if the 0th board (L board) is in the data
                if 0 in data_point["data"].keys():
                    board_left = " ".join(
                        [chain["chip_status"] for chain in data_point["data"][0]]
                    ).replace("o", "•")
                else:
                    # if the board isn't in data, highlight it red
                    row_colors.append((ip_table_index, "bad"))

                # check if the 1st board (C board) is in the data
                if 1 in data_point["data"].keys():
                    board_center = " ".join(
                        [chain["chip_status"] for chain in data_point["data"][1]]
                    ).replace("o", "•")
                else:
                    # if the board isn't in data, highlight it red
                    row_colors.append((ip_table_index, "bad"))

                # check if the 2nd board (R board) is in the data
                if 2 in data_point["data"].keys():
                    board_right = " ".join(
                        [chain["chip_status"] for chain in data_point["data"][2]]
                    ).replace("o", "•")
                else:
                    # if the board isn't in data, highlight it red
                    row_colors.append((ip_table_index, "bad"))

                # check if the miner has all nominal chips
                if False in [
                    # True/False if the miner is nominal
                    chain["nominal"]
                    # for each board in the miner
                    for board in [
                        data_point["data"][key] for key in data_point["data"].keys()
                    ]
                    # for each chain in each board in the miner
                    for chain in board
                ]:
                    # if the miner doesn't have all chips, highlight it red
                    row_colors.append((ip_table_index, "bad"))
            else:
                # the row is bad if we have no data
                row_colors.append((ip_table_index, "bad"))

            # split the chip data into thirds
            board_left_chips = "\n".join(split_chips(board_left, 3))
            board_center_chips = "\n".join(split_chips(board_center, 3))
            board_right_chips = "\n".join(split_chips(board_right, 3))

            # create data for the table
            data = [
                data_point["IP"],
                data_point["model"],
                (len(board_left) + len(board_center) + len(board_right)),
                len(board_left),
                board_left_chips,
                len(board_center),
                board_center_chips,
                len(board_right),
                board_right_chips,
            ]

            # put the data at the index of the IP address
            ip_table_data[ip_table_index] = data
            window["ip_table"].update(ip_table_data)

            # configure "bad" tag to highlight red
            table = window["ip_table"].Widget
            table.tag_configure("bad", foreground="white", background="red")

            # set tags on the row if they have been set
            for row in row_colors:
                table.item(row[0] + 1, tags=row[1])

        # add to the progress bar
        progress_bar_len += 1
        asyncio.create_task(update_prog_bar(progress_bar_len))

    # reset status
    await update_ui_with_data("status", "")


def split_chips(string, number_of_splits):
    k, m = divmod(len(string), number_of_splits)
    return (
        string[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
        for i in range(number_of_splits)
    )


async def get_formatted_data(ip: ipaddress.ip_address):
    miner = await MinerFactory().get_miner(ip)
    model = await miner.get_model()
    warnings.filterwarnings("ignore")
    board_data = await miner.get_board_info()
    data = {"IP": str(ip), "model": str(model), "data": board_data}
    return data
