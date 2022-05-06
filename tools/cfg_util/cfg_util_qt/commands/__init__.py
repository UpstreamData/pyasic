from miners.miner_factory import MinerFactory
from tools.cfg_util.cfg_util_qt.layout import window
from tools.cfg_util.cfg_util_qt.tables import TableManager
from tools.cfg_util.cfg_util_qt.decorators import disable_buttons


@disable_buttons
async def btn_light(ips: list):
    table_manager = TableManager()
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    for idx in ips:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        new_light_val = not table_manager.data[ip]["Light"]
        miner = await MinerFactory().get_miner(ip)
        if new_light_val:
            success = await miner.fault_light_on()
        else:
            success = await miner.fault_light_off()
        if success:
            table_manager.data[ip]["Light"] = new_light_val
            table_manager.data[ip]["Command Output"] = "Fault Light command succeeded."
        else:
            table_manager.data[ip]["Command Output"] = "Fault Light command failed."
    table_manager.update_tables()
