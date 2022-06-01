import asyncio
import webbrowser

from miners.miner_factory import MinerFactory
from tools.cfg_util.decorators import disable_buttons
from tools.cfg_util.layout import TABLE_KEYS
from tools.cfg_util.layout import window, update_prog_bar, TABLE_HEADERS
from tools.cfg_util.tables import TableManager, DATA_HEADER_MAP

progress_bar_len = 0

headers = []
for key in TABLE_HEADERS.keys():
    for item in TABLE_HEADERS[key]:
        headers.append(item)

DEFAULT_DATA = set(headers)


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


@disable_buttons("Refreshing")
async def btn_refresh(table, selected):
    ips = [window[table].Values[row][0] for row in selected]
    if not len(selected) > 0:
        ips = [window[table].Values[row][0] for row in range(len(window[table].Values))]

    await update_miners_data(ips)


async def update_miners_data(miners: list):
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
    await update_prog_bar(progress_bar_len, _max=len(miners))
    data_generator = asyncio.as_completed(
        [_get_data(await MinerFactory().get_miner(miner)) for miner in miners]
    )
    for all_data in data_generator:
        data = await all_data
        TableManager().update_item(data)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)


async def _get_data(miner):
    _data = (await miner.get_data()).asdict()
    data = {}
    for item in _data.keys():
        if item in DATA_HEADER_MAP.keys():
            data[DATA_HEADER_MAP[item]] = _data[item]
    return data
