import asyncio
import webbrowser

from miners.miner_factory import MinerFactory
from tools.cfg_util.cfg_util_qt.decorators import disable_buttons
from tools.cfg_util.cfg_util_qt.layout import TABLE_KEYS
from tools.cfg_util.cfg_util_qt.layout import window, update_prog_bar
from tools.cfg_util.cfg_util_qt.tables import TableManager

progress_bar_len = 0

DEFAULT_DATA = [
    "Model",
    "Hostname",
    "Hashrate",
    "Temperature",
    "Pool User",
    "Pool 1",
    "Pool 1 User",
    "Pool 2",
    "Pool 2 User",
    "Wattage",
    "Split",
]


def btn_all(table, selected):
    if table in TABLE_KEYS["table"]:
        if len(selected) == len(window[table].Values):
            window[table].update(select_rows=())
        else:
            window[table].update(
                select_rows=([row for row in range(len(window[table].Values))])
            )

    if table in TABLE_KEYS["tree"]:
        if len(selected) == len(window[table].Widget.get_children()):
            _tree = window[table]
            _tree.Widget.selection_set([])
        else:
            _tree = window[table]
            rows_to_select = [i for i in _tree.Widget.get_children()]
            _tree.Widget.selection_set(rows_to_select)


def btn_web(table, selected):
    for row in selected:
        webbrowser.open("http://" + window[table].Values[row][0])


@disable_buttons
async def btn_refresh(table, selected):
    ips = [window[table].Values[row][0] for row in selected]
    if not len(selected) > 0:
        ips = [window[table].Values[row][0] for row in range(len(window[table].Values))]

    await _get_miners_data(ips)


async def _get_miners_data(miners: list):
    data = []
    for miner in miners:
        _data = {}
        for key in DEFAULT_DATA:
            _data[key] = ""
        _data["IP"] = str(miner)
        data.append(_data)

    TableManager().update_data(data)

    global progress_bar_len
    progress_bar_len = 0
    await update_prog_bar(progress_bar_len, max=len(miners))
    data_generator = asyncio.as_completed(
        [_get_data(await MinerFactory().get_miner(miner)) for miner in miners]
    )
    for all_data in data_generator:
        data = await all_data
        TableManager().update_item(data)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)


async def _get_data(miner):
    return await miner.get_data()
