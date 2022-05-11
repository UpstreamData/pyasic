from miners.miner_factory import MinerFactory
from tools.cfg_util.layout import window
from tools.cfg_util.tables import TableManager
from tools.cfg_util.decorators import disable_buttons


@disable_buttons("Flashing Lights")
async def btn_light(ip_idxs: list):
    table_manager = TableManager()
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    for idx in ip_idxs:
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
            table_manager.data[ip]["Output"] = "Fault Light command succeeded."
        else:
            table_manager.data[ip]["Output"] = "Fault Light command failed."
    table_manager.update_tables()


@disable_buttons("Rebooting")
async def btn_reboot(ip_idxs: list):
    table_manager = TableManager()
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        miner = await MinerFactory().get_miner(ip)
        success = await miner.reboot()
        if success:
            table_manager.data[ip]["Output"] = "Reboot command succeeded."
        else:
            table_manager.data[ip]["Output"] = "Reboot command failed."
    table_manager.update_tables()


@disable_buttons("Restarting Backend")
async def btn_backend(ip_idxs: list):
    table_manager = TableManager()
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        miner = await MinerFactory().get_miner(ip)
        success = await miner.restart_backend()
        if success:
            table_manager.data[ip]["Output"] = "Restart Backend command succeeded."
        else:
            table_manager.data[ip]["Output"] = "Restart Backend command failed."
    table_manager.update_tables()


@disable_buttons("Sending Command")
async def btn_command(ip_idxs: list, command: str):
    table_manager = TableManager()
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        miner = await MinerFactory().get_miner(ip)
        success = await miner.send_ssh_command(command)
        if not isinstance(success, str):
            success = f"Command {command} failed."
        table_manager.data[ip]["Output"] = success
    table_manager.update_tables()
