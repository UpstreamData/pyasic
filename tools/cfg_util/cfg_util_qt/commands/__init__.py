from tools.cfg_util.cfg_util_qt.layout import window
from tools.cfg_util.cfg_util_qt.tables import update_tree
from tools.cfg_util.cfg_util_qt.imgs import TkImages


async def btn_light(ips: list):
    _table = window["cmd_table"].Widget
    data = []
    iids = _table.get_children()
    for idx in ips:
        item = _table.item(iids[idx])
        data.append(
            {
                "IP": item["values"][0],
                "Model": item["values"][1],
                "Command Output": item["values"][2],
                "Light": True,
            }
        )
    await update_tree(data)
