import PySimpleGUI as sg
from config.bos import bos_config_convert
import time
from tools.cfg_util.cfg_util_qt.layout import window


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
