import PySimpleGUI as sg
from .imgs import WINDOW_ICON, LIGHT, FAULT_LIGHT

TABLE_HEADERS = {
    "SCAN": [
        "IP",
        "Model",
        "Hostname",
        "Hashrate",
        "Temperature",
        "Pool User",
        "Wattage",
    ],
    "CMD": ["IP", "Model", "Command Output"],
    "POOLS": [
        "IP",
        "Split",
        "Pool 1",
        "Pool 1 User",
        "Pool 2",
        "Pool 2 User",
    ],
    "CONFIG": ["IP", "Model", "Pool 1 User"],
}

TABLE_KEYS = {
    "table": ["scan_table", "pools_table", "cfg_table"],
    "tree": ["cmd_table"],
}

MINER_COUNT_BUTTONS = [
    "scan_miner_count",
    "cmd_miner_count",
    "cfg_miner_count",
    "pools_miner_count",
]

BUTTON_KEYS = [
    "btn_scan",
    "btn_cmd",
    "scan_all",
    "scan_refresh",
    "scan_web",
    "cmd_all",
    "cmd_light",
    "cmd_reboot",
    "cmd_backend",
    "pools_all",
    "pools_refresh",
    "pools_web",
    "cfg_import",
    "cfg_config",
    "cfg_generate",
    "cfg_all",
    "cfg_web",
]

TABLE_HEIGHT = 27

IMAGE_COL_WIDTH = 6
IP_COL_WIDTH = 17
MODEL_COL_WIDTH = 15
HOST_COL_WIDTH = 15
HASHRATE_COL_WIDTH = 12
TEMP_COL_WIDTH = 12
USER_COL_WIDTH = 31
WATTAGE_COL_WIDTH = 8
SPLIT_COL_WIDTH = 6
SCAN_COL_WIDTHS = [
    IP_COL_WIDTH,
    MODEL_COL_WIDTH,
    HOST_COL_WIDTH,
    HASHRATE_COL_WIDTH,
    TEMP_COL_WIDTH,
    USER_COL_WIDTH,
    WATTAGE_COL_WIDTH,
]
TABLE_TOTAL_WIDTH = sum(SCAN_COL_WIDTHS)


async def update_prog_bar(count: int, max: int = None):
    bar = window["progress_bar"]
    bar.update_bar(count, max=max)
    if not hasattr(bar, "maxlen"):
        if not max:
            max = 100
        bar.maxlen = max
    percent_done = 100 * (count / bar.maxlen)
    window["progress_percent"].Update(f"{round(percent_done, 2)} %")
    if percent_done == 100:
        window["progress_percent"].Update("")


def get_scan_layout():
    scan_layout = [
        [
            sg.Text("Scan IP"),
            sg.InputText(key="scan_ip", size=(31, 1)),
            sg.Button("Scan", key="btn_scan"),
            sg.Push(),
            sg.Button(
                "Miners: 0",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="scan_miner_count",
            ),
        ],
        [
            sg.Button("ALL", key="scan_all"),
            sg.Button("REFRESH DATA", key="scan_refresh"),
            sg.Button("OPEN IN WEB", key="scan_web"),
        ],
        [
            sg.Table(
                values=[],
                headings=[heading for heading in TABLE_HEADERS["SCAN"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="scan_table",
                col_widths=SCAN_COL_WIDTHS,
                background_color="white",
                text_color="black",
                size=(TABLE_TOTAL_WIDTH, TABLE_HEIGHT),
                expand_x=True,
                enable_click_events=True,
            )
        ],
    ]
    return scan_layout


def get_command_layout():
    data = sg.TreeData()
    col_widths = [
        IP_COL_WIDTH,
        MODEL_COL_WIDTH,
        TABLE_TOTAL_WIDTH - (IP_COL_WIDTH + MODEL_COL_WIDTH + IMAGE_COL_WIDTH + 4),
    ]

    command_layout = [
        [
            sg.Text("Custom Command"),
            sg.InputText(key="cmd_txt", expand_x=True),
            sg.Button("Send Command", key="btn_cmd"),
            sg.Push(),
            sg.Button(
                "Miners: 0",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="cmd_miner_count",
            ),
        ],
        [
            sg.Button("ALL", key="cmd_all"),
            sg.Button("LIGHT", key="cmd_light"),
            sg.Button("REBOOT", key="cmd_reboot"),
            sg.Button("RESTART BACKEND", key="cmd_backend"),
        ],
        [
            sg.Tree(
                data,
                headings=[heading for heading in TABLE_HEADERS["CMD"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="cmd_table",
                col_widths=col_widths,
                background_color="white",
                text_color="black",
                expand_x=True,
                expand_y=True,
                col0_heading="Light",
                col0_width=IMAGE_COL_WIDTH,
                enable_events=True,
            )
        ],
    ]
    return command_layout


def get_pools_layout():
    pool_col_width = int((TABLE_TOTAL_WIDTH - (IP_COL_WIDTH + SPLIT_COL_WIDTH)) / 4)
    col_widths = [
        IP_COL_WIDTH,
        SPLIT_COL_WIDTH,
        pool_col_width + 5,
        pool_col_width - 5,
        pool_col_width + 5,
        pool_col_width - 5,
    ]
    pools_layout = [
        [
            sg.Push(),
            sg.Button(
                "Miners: 0",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="pools_miner_count",
            ),
        ],
        [
            sg.Button("ALL", key="pools_all"),
            sg.Button("REFRESH DATA", key="pools_refresh"),
            sg.Button("OPEN IN WEB", key="pools_web"),
        ],
        [
            sg.Table(
                values=[],
                headings=[heading for heading in TABLE_HEADERS["POOLS"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="pools_table",
                background_color="white",
                text_color="black",
                col_widths=col_widths,
                size=(0, TABLE_HEIGHT),
                expand_x=True,
                enable_click_events=True,
            )
        ],
    ]
    return pools_layout


def get_config_layout():
    config_layout = [
        [
            sg.Button("IMPORT", key="cfg_import"),
            sg.Button("CONFIG", key="cfg_config"),
            sg.Button("GENERATE", key="cfg_generate"),
            sg.Push(),
            sg.Button(
                "Miners: 0",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="cfg_miner_count",
            ),
        ],
        [
            sg.Button("ALL", key="cfg_all"),
            sg.Button("OPEN IN WEB", key="cfg_web"),
            sg.Push(),
            sg.Checkbox("Append IP to Username", key="cfg_append_ip"),
        ],
        [
            sg.Table(
                values=[],
                headings=[heading for heading in TABLE_HEADERS["CONFIG"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="cfg_table",
                background_color="white",
                text_color="black",
                col_widths=[
                    IP_COL_WIDTH,
                    MODEL_COL_WIDTH,
                    TABLE_TOTAL_WIDTH - ((2 * 40) - 4),
                ],
                size=(0, TABLE_HEIGHT),
                expand_x=True,
                enable_click_events=True,
            ),
            sg.Multiline(size=(40, TABLE_HEIGHT + 1)),
        ],
    ]
    return config_layout


layout = [
    [
        sg.Text("", size=(10, 1), key="status"),
        sg.ProgressBar(
            max_value=100, size_px=(0, 20), expand_x=True, key="progress_bar"
        ),
        sg.Text("", size=(10, 1), key="progress_percent"),
    ],
    [
        sg.TabGroup(
            [
                [sg.Tab("Scan", get_scan_layout())],
                [sg.Tab("Pools", get_pools_layout())],
                [sg.Tab("Configure", get_config_layout())],
                [sg.Tab("Command", get_command_layout())],
            ]
        )
    ],
]

window = sg.Window("Upstream Config Util", layout, icon=WINDOW_ICON)
