import asyncio

import PySimpleGUI as sg

from config import MinerConfig
from miners.miner_factory import MinerFactory
from settings import CFG_UTIL_CONFIG_THREADS as CONFIG_THREADS
from tools.cfg_util.decorators import disable_buttons
from tools.cfg_util.general import update_miners_data
from tools.cfg_util.layout import window, update_prog_bar

progress_bar_len = 0


@disable_buttons("Importing")
async def btn_import(table, selected):
    if not len(selected) > 0:
        return
    ip = [window[table].Values[row][0] for row in selected][0]
    miner = await MinerFactory().get_miner(ip)
    await miner.get_config()
    config = miner.config
    if config:
        window["cfg_config_txt"].update(config.as_yaml())


@disable_buttons("Configuring")
async def btn_config(table, selected, config: str, last_oct_ip: bool):
    ips = [window[table].Values[row][0] for row in selected]
    await send_config(ips, config, last_oct_ip)


async def send_config(ips: list, config: str, last_octet_ip: bool):
    global progress_bar_len
    progress_bar_len = 0
    await update_prog_bar(progress_bar_len, _max=(2 * len(ips)))
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


def generate_config(
    username: str,
    workername: str,
    v2_allowed: bool,
    advanced_cfg: bool,
    autotuning_enabled: bool,
    autotuning_wattage: int,
    manual_fan_control: bool,
    manual_fan_speed: int,
    min_fans: int,
    target_temp: int,
    hot_temp: int,
    dangerous_temp: int,
    dps_enabled: bool,
    dps_power_step: int,
    dps_min_power: int,
    dps_shutdown_enabled: bool,
    dps_shutdown_duration: int,
):
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
    if not advanced_cfg:
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
            "temp_control": {
                "target_temp": 80.0,
                "hot_temp": 90.0,
                "dangerous_temp": 120.0,
            },
            "autotuning": {"enabled": True, "psu_power_limit": 900},
        }
    else:
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
            "temp_control": {
                "mode": "auto",
                "target_temp": float(target_temp),
                "hot_temp": float(hot_temp),
                "dangerous_temp": float(dangerous_temp),
            },
            "autotuning": {
                "enabled": autotuning_enabled,
                "psu_power_limit": autotuning_wattage,
            },
        }
        if manual_fan_control:
            config["temp_control"]["mode"] = "manual"
            config["fan_control"] = {}
            config["fan_control"]["speed"] = manual_fan_speed
            config["fan_control"]["min_fans"] = min_fans
        if dps_enabled:
            config["power_scaling"] = {
                "enabled": dps_enabled,
                "power_step": dps_power_step,
                "min_psu_power_limit": dps_min_power,
                "shutdown_enabled": dps_shutdown_enabled,
                "shutdown_duration": dps_shutdown_duration,
            }

    cfg = MinerConfig().from_raw(config)

    window["cfg_config_txt"].update(cfg.as_yaml())


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
                    values["show_advanced_options"],
                    values["autotuning_enabled"],
                    values["autotuning_wattage"],
                    values["manual_fan_control"],
                    values["manual_fan_speed"],
                    values["min_fans"],
                    values["target_temp"],
                    values["hot_temp"],
                    values["danger_temp"],
                    values["dps_enabled"],
                    values["dps_power_step"],
                    values["dps_min_power"],
                    values["dps_shutdown_enabled"],
                    values["dps_shutdown_duration"],
                )
                generate_config_window.close()
                break
        if event == "show_advanced_options":
            generate_config_window["advanced_options"].update(
                visible=values["show_advanced_options"]
            )

        if event == "autotuning_enabled":
            generate_config_window["autotuning_wattage"].update(
                disabled=not values["autotuning_enabled"]
            )
        if event == "manual_fan_control":
            generate_config_window["manual_fan_speed"].update(
                disabled=not values["manual_fan_control"]
            )
            generate_config_window["min_fans"].update(
                disabled=not values["manual_fan_control"]
            )
        if event == "dps_enabled":
            for elem in ["dps_power_step", "dps_min_power", "dps_shutdown_enabled"]:
                generate_config_window[elem].update(disabled=not values["dps_enabled"])
            if not values["dps_enabled"]:
                generate_config_window["dps_shutdown_duration"].update(disabled=True)
            if values["dps_enabled"] and values["dps_shutdown_enabled"]:
                generate_config_window["dps_shutdown_duration"].update(disabled=False)
        if event == "dps_shutdown_enabled":
            if values["dps_enabled"]:
                generate_config_window["dps_shutdown_duration"].update(
                    disabled=not values["dps_shutdown_enabled"]
                )


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
        [
            sg.Push(),
            sg.Checkbox(
                "Advanced Options", enable_events=True, key="show_advanced_options"
            ),
        ],
        [
            sg.pin(
                sg.Column(
                    [
                        [
                            sg.Text("Autotuning Enabled:", size=(19, 1)),
                            sg.Checkbox(
                                "", key="autotuning_enabled", enable_events=True
                            ),
                            sg.Text("Power Limit:"),
                            sg.Spin(
                                [i for i in range(100, 5001, 100)],
                                initial_value=900,
                                size=(5, 1),
                                key="autotuning_wattage",
                                disabled=True,
                            ),
                        ],
                        [
                            sg.Text("Manual Fan Control:", size=(19, 1)),
                            sg.Checkbox(
                                "", key="manual_fan_control", enable_events=True
                            ),
                            sg.Text("Speed:"),
                            sg.Spin(
                                [i for i in range(5, 101, 5)],
                                initial_value=100,
                                size=(5, 1),
                                key="manual_fan_speed",
                                disabled=True,
                            ),
                            sg.Text("Min Fans:"),
                            sg.Spin(
                                [i for i in range(5)],
                                initial_value=1,
                                size=(5, 1),
                                key="min_fans",
                                disabled=True,
                            ),
                        ],
                        [
                            sg.Text("Target Temp:", size=(19, 1)),
                            sg.Spin(
                                [i for i in range(5, 101, 5)],
                                initial_value=80,
                                size=(5, 1),
                                key="target_temp",
                            ),
                        ],
                        [
                            sg.Text("Hot Temp:", size=(19, 1)),
                            sg.Spin(
                                [i for i in range(5, 111, 5)],
                                initial_value=90,
                                size=(5, 1),
                                key="hot_temp",
                            ),
                        ],
                        [
                            sg.Text("Dangerous Temp:", size=(19, 1)),
                            sg.Spin(
                                [i for i in range(5, 131, 5)],
                                initial_value=100,
                                size=(5, 1),
                                key="danger_temp",
                            ),
                        ],
                        [
                            sg.Text("Dynamic Power Scaling:"),
                            sg.Checkbox("", key="dps_enabled", enable_events=True),
                            sg.Text("Power Step:"),
                            sg.Spin(
                                [i for i in range(50, 301, 5)],
                                initial_value=100,
                                size=(5, 1),
                                key="dps_power_step",
                                disabled=True,
                            ),
                            sg.Text("Min Power:"),
                            sg.Spin(
                                [i for i in range(100, 5001, 100)],
                                initial_value=800,
                                size=(5, 1),
                                key="dps_min_power",
                                disabled=True,
                            ),
                        ],
                        [
                            sg.Text("DPS Shutdown:"),
                            sg.Checkbox(
                                "",
                                key="dps_shutdown_enabled",
                                enable_events=True,
                                disabled=True,
                            ),
                            sg.Text("Shutdown Duration (H):"),
                            sg.Spin(
                                [i for i in range(1, 11, 1)],
                                initial_value=3,
                                size=(5, 1),
                                key="dps_shutdown_duration",
                                disabled=True,
                            ),
                        ],
                    ],
                    key="advanced_options",
                    visible=False,
                    pad=0,
                )
            )
        ],
        [sg.Button("Generate", key="generate_config_window_generate")],
    ]
    return config_layout
