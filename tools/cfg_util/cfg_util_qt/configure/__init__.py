import PySimpleGUI as sg
from config.bos import bos_config_convert
import time
from tools.cfg_util.cfg_util_qt.layout import window, update_prog_bar
from tools.cfg_util.cfg_util_qt.decorators import disable_buttons
from miners.miner_factory import MinerFactory
import asyncio
from settings import CFG_UTIL_CONFIG_THREADS as CONFIG_THREADS
from tools.cfg_util.cfg_util_qt.general import update_miners_data


progress_bar_len = 0


@disable_buttons("Importing")
async def btn_import(table, selected):
    if not len(selected) > 0:
        return
    ip = [window[table].Values[row][0] for row in selected][0]
    miner = await MinerFactory().get_miner(ip)
    await miner.get_config()
    config = miner.config
    window["cfg_config_txt"].update(config)


@disable_buttons("Configuring")
async def btn_config(table, selected, config: str, last_oct_ip: bool):
    ips = [window[table].Values[row][0] for row in selected]
    await send_config(ips, config, last_oct_ip)


async def send_config(ips: list, config: str, last_octet_ip: bool):
    global progress_bar_len
    progress_bar_len = 0
    await update_prog_bar(progress_bar_len, max=(2 * len(ips)))
    get_miner_genenerator = MinerFactory().get_miner_generator(ips)
    all_miners = []
    async for miner in get_miner_genenerator:
        all_miners.append(miner)
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)

    config_sender_generator = send_config_generator(
        all_miners, config, last_octet_ip_user=last_octet_ip
    )
    async for _config_sender in config_sender_generator:
        progress_bar_len += 1
        await update_prog_bar(progress_bar_len)
    await asyncio.sleep(3)
    await update_miners_data(ips)


async def send_config_generator(miners: list, config, last_octet_ip_user: bool):
    loop = asyncio.get_event_loop()
    config_tasks = []
    for miner in miners:
        if len(config_tasks) >= CONFIG_THREADS:
            configured = asyncio.as_completed(config_tasks)
            config_tasks = []
            for sent_config in configured:
                yield await sent_config
        config_tasks.append(
            loop.create_task(miner.send_config(config, ip_user=last_octet_ip_user))
        )
    configured = asyncio.as_completed(config_tasks)
    for sent_config in configured:
        yield await sent_config


def generate_config(username: str, workername: str, v2_allowed: bool):
    if username and workername:
        user = f"{username}.{workername}"
    elif username and not workername:
        user = username
    else:
        return

    if v2_allowed:
        url_1 = "stratum2+tcp://v2.us-east.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt"
        url_2 = "stratum2+tcp://v2.stratum.slushpool.com/u95GEReVMjK6k5YqiSFNqqTnKU4ypU2Wm8awa6tmbmDmk1bWt"
        url_3 = "stratum+tcp://stratum.slushpool.com:3333"
    else:
        url_1 = "stratum+tcp://ca.stratum.slushpool.com:3333"
        url_2 = "stratum+tcp://us-east.stratum.slushpool.com:3333"
        url_3 = "stratum+tcp://stratum.slushpool.com:3333"

    config = {
        "group": [
            {
                "name": "group",
                "quota": 1,
                "pool": [
                    {"url": url_1, "user": user, "password": "123"},
                    {"url": url_2, "user": user, "password": "123"},
                    {"url": url_3, "user": user, "password": "123"},
                ],
            }
        ],
        "format": {
            "version": "1.2+",
            "model": "Antminer S9",
            "generator": "upstream_config_util",
            "timestamp": int(time.time()),
        },
        "temp_control": {
            "target_temp": 80.0,
            "hot_temp": 90.0,
            "dangerous_temp": 120.0,
        },
        "autotuning": {"enabled": True, "psu_power_limit": 900},
    }
    window["cfg_config_txt"].update(bos_config_convert(config))


async def generate_config_ui():
    generate_config_window = sg.Window(
        "Generate Config", generate_config_layout(), modal=True
    )
    while True:
        event, values = generate_config_window.read()
        if event in (None, "Close", sg.WIN_CLOSED):
            break
        if event == "generate_config_window_generate":
            if values["generate_config_window_username"]:
                generate_config(
                    values["generate_config_window_username"],
                    values["generate_config_window_workername"],
                    values["generate_config_window_allow_v2"],
                )
                generate_config_window.close()
                break


def generate_config_layout():
    config_layout = [
        [
            sg.Text(
                "Enter your pool username and password below to generate a config for SlushPool."
            )
        ],
        [sg.Text("")],
        [
            sg.Text("Username:", size=(19, 1)),
            sg.InputText(
                key="generate_config_window_username", do_not_clear=True, size=(45, 1)
            ),
        ],
        [
            sg.Text("Worker Name (OPT):", size=(19, 1)),
            sg.InputText(
                key="generate_config_window_workername", do_not_clear=True, size=(45, 1)
            ),
        ],
        [
            sg.Text("Allow Stratum V2?:", size=(19, 1)),
            sg.Checkbox("", key="generate_config_window_allow_v2", default=True),
        ],
        [sg.Button("Generate", key="generate_config_window_generate")],
    ]
    return config_layout
