from miners.miner_factory import MinerFactory
from miners.miner_listener import MinerListener
from tools.cfg_util.layout import window, update_prog_bar, WINDOW_ICON
from tools.cfg_util.tables import TableManager
from tools.cfg_util.decorators import disable_buttons
from settings import CFG_UTIL_CONFIG_THREADS as COMMAND_THREADS
from typing import Tuple

import PySimpleGUI as sg

import asyncio


@disable_buttons("Flashing Lights")
async def btn_light(ip_idxs: list):
    table_manager = TableManager()
    _table = window["cmd_table"].Widget
    iids = _table.get_children()
    tasks = []
    vals = {}
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        new_light_val = not table_manager.data[ip]["Light"]
        tasks.append(_fault_light(ip, new_light_val))
        vals[ip] = new_light_val

    for task in asyncio.as_completed(tasks):
        ip, success = await task
        if success:
            table_manager.data[ip]["Light"] = vals[ip]
            table_manager.data[ip]["Output"] = "Fault Light command succeeded."
        else:
            table_manager.data[ip]["Output"] = "Fault Light command failed."
        table_manager.update_tables()


async def _fault_light(ip: str, on: bool) -> Tuple[str, bool]:
    miner = await MinerFactory().get_miner(ip)
    if on:
        success = await miner.fault_light_on()
    else:
        success = await miner.fault_light_off()
    return miner.ip, success


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
    prog_bar_len = 0
    await update_prog_bar(prog_bar_len, len(ip_idxs))
    table_manager = TableManager()
    _table = window["cmd_table"].Widget
    miners = []
    iids = _table.get_children()
    for idx in ip_idxs:
        item = _table.item(iids[idx])
        ip = item["values"][0]
        miner = await MinerFactory().get_miner(ip)
        miners.append(miner)

    sent = send_command_generator(miners, command)
    async for done in sent:
        success = done["Status"]
        if not isinstance(done["Status"], str):
            success = f"Command {command} failed."
        table_manager.data[done["IP"]]["Output"] = success
        prog_bar_len += 1
        table_manager.update_tables()
        await update_prog_bar(prog_bar_len, len(ip_idxs))


async def send_command_generator(miners: list, command: str):
    loop = asyncio.get_event_loop()
    command_tasks = []
    for miner in miners:
        if len(command_tasks) >= COMMAND_THREADS:
            cmd_sent = asyncio.as_completed(command_tasks)
            command_tasks = []
            for done in cmd_sent:
                yield await done
        command_tasks.append(loop.create_task(_send_ssh_command(miner, command)))
    cmd_sent = asyncio.as_completed(command_tasks)
    for done in cmd_sent:
        yield await done


async def _send_ssh_command(miner, command: str):
    proc = await miner.send_ssh_command(command)
    return {"IP": miner.ip, "Status": proc}


CANCEL_LISTEN_BTNS = [
    "cmd_cancel_listen",
    "pools_cancel_listen",
    "boards_cancel_listen",
    "scan_cancel_listen",
    "cfg_cancel_listen",
]


@disable_buttons("Listening for Miner")
async def btn_listen():
    window["cmd_listen"].update(visible=False)
    for btn in CANCEL_LISTEN_BTNS:
        window[btn].update(visible=True)
    async for miner in MinerListener().listen():
        sg.popup(
            f"IP: {miner['IP']}, MAC: {miner['MAC']}",
            title="Found Miner",
            keep_on_top=True,
            icon=WINDOW_ICON,
        )


async def btn_cancel_listen():
    await MinerListener().cancel()
    window["cmd_listen"].update(visible=True)
    for btn in CANCEL_LISTEN_BTNS:
        window[btn].update(visible=False)
