import PySimpleGUI as sg

from .imgs import WINDOW_ICON

WINDOW_BG = "#0F4C75"

PROGRESS_BG = "#FFFFFF"
PROGRESS_FULL = "#00A8CC"

MAIN_TABS_BG = "#0F4C75"
MAIN_TABS_SELECTED = MAIN_TABS_BG
MAIN_TABS_NORMAL = "#BBE1FA"
MAIN_TABS_TEXT_SELECTED = "#FFFFFF"
MAIN_TABS_TEXT_NORMAL = "#000000"

TEXT_COLOR = "#FFFFFF"

BTN_TEXT_COLOR = "#000000"
BTN_COLOR = "#3282B8"
BTN_DISABLED_COLOR = "#BBE1FA"
BTN_DISABLED_TEXT_COLOR = "#1B262C"
BTN_DISABLED = BTN_DISABLED_TEXT_COLOR, BTN_DISABLED_COLOR
BTN_BORDER = 1

INFO_BTN_TEXT_COLOR = "#000000"
INFO_BTN_BG = "#FFFFFF"

INPUT_BG = "#BBE1FA"
INPUT_TEXT = "#000000"

POOLS_TABS_BG = "#3282B8"
POOLS_TABS_SELECTED = POOLS_TABS_BG
POOLS_TABS_NORMAL = "#BBE1FA"
POOLS_TABS_TEXT_SELECTED = "#FFFFFF"
POOLS_TABS_TEXT_NORMAL = "#000000"

TABLE_BG = "#BBE1FA"
TABLE_TEXT = "#000000"
TABLE_HEADERS_COLOR = "#3282B8"
TABLE_HEADERS_TEXT_COLOR = "#000000"
TABLE_HEADERS_HOVER = "#27496D"
TABLE_BORDER = 1
TABLE_HEADER_BORDER = 3

POOLS_TABLE_BG = TABLE_BG
POOLS_TABLE_TEXT = TABLE_TEXT
POOLS_TABLE_HEADERS_COLOR = TABLE_HEADERS_COLOR
POOLS_TABLE_HEADERS_TEXT_COLOR = TABLE_HEADERS_TEXT_COLOR
POOLS_TABLE_HEADERS_HOVER = TABLE_HEADERS_HOVER
POOLS_TABLE_BORDER = 1
POOLS_TABLE_HEADER_BORDER = 3

sg.set_options(font=("Noto Mono", 10))
# Add your new theme colors and settings


sg.LOOK_AND_FEEL_TABLE["cfg_util_theme"] = {
    "BACKGROUND": WINDOW_BG,
    "TEXT": TEXT_COLOR,
    "INPUT": INPUT_BG,
    "TEXT_INPUT": INPUT_TEXT,
    "SCROLL": "#142850",
    "BUTTON": (BTN_TEXT_COLOR, BTN_COLOR),  # Text Color, Background
    "PROGRESS": (PROGRESS_FULL, PROGRESS_BG),  # Filled, Empty
    "BORDER": 1,
    "SLIDER_DEPTH": 0,
    "PROGRESS_DEPTH": 0,
}

# Switch to use your newly created theme
sg.theme("cfg_util_theme")

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
    "CMD": ["IP", "Model", "Output"],
    "POOLS_ALL": [
        "IP",
        "Split",
        "Pool 1 User",
        "Pool 2 User",
    ],
    "POOLS_1": [
        "IP",
        "Split",
        "Pool 1",
        "Pool 1 User",
    ],
    "POOLS_2": [
        "IP",
        "Split",
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

SORT_KEY_BUTTONS = [
    "scan_sort_key",
    "cmd_sort_key",
    "cfg_sort_key",
    "pools_sort_key",
]

HASHRATE_TOTAL_BUTTONS = [
    "scan_total_hashrate",
    "cfg_total_hashrate",
    "pools_total_hashrate",
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
    if max:
        bar.maxlen = max
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
            sg.Text("Scan IP", background_color=MAIN_TABS_BG),
            sg.InputText(key="scan_ip", size=(31, 1)),
            sg.Button(
                "Scan",
                key="btn_scan",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
                mouseover_colors=BTN_DISABLED,
            ),
            sg.Push(background_color=MAIN_TABS_BG),
            sg.Button(
                "Sort: IP",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="scan_sort_key",
            ),
            sg.Button(
                "Hashrate: 0 TH/s",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="scan_total_hashrate",
            ),
            sg.Button(
                "Miners: 0",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="scan_miner_count",
            ),
        ],
        [
            sg.Button(
                "ALL",
                key="scan_all",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "REFRESH DATA",
                key="scan_refresh",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "OPEN IN WEB",
                key="scan_web",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
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
                background_color=TABLE_BG,
                text_color=TABLE_TEXT,
                header_background_color=TABLE_HEADERS_COLOR,
                header_text_color=TABLE_HEADERS_TEXT_COLOR,
                border_width=TABLE_BORDER,
                header_border_width=TABLE_HEADER_BORDER,
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
            sg.Text("Custom Command", background_color=MAIN_TABS_BG),
            sg.InputText(key="cmd_txt", expand_x=True),
            sg.Button(
                "Send Command",
                key="btn_cmd",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Push(background_color=MAIN_TABS_BG),
            sg.Button(
                "Sort: IP",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="cmd_sort_key",
            ),
            sg.Button(
                "Miners: 0",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="cmd_miner_count",
            ),
        ],
        [
            sg.Button(
                "ALL",
                key="cmd_all",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "LIGHT",
                key="cmd_light",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "REBOOT",
                key="cmd_reboot",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "RESTART BACKEND",
                key="cmd_backend",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
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
                background_color=TABLE_BG,
                text_color=TABLE_TEXT,
                header_background_color=TABLE_HEADERS_COLOR,
                header_text_color=TABLE_HEADERS_TEXT_COLOR,
                border_width=TABLE_BORDER,
                header_border_width=TABLE_HEADER_BORDER,
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
    pool_col_width = int((TABLE_TOTAL_WIDTH - (IP_COL_WIDTH + SPLIT_COL_WIDTH)) / 2)
    col_widths = [
        IP_COL_WIDTH,
        SPLIT_COL_WIDTH,
        pool_col_width,
        pool_col_width,
    ]
    pools_layout = [
        [
            sg.Button(
                "ALL",
                key="pools_all",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "REFRESH DATA",
                key="pools_refresh",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "OPEN IN WEB",
                key="pools_web",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Push(background_color=MAIN_TABS_BG),
            sg.Button(
                "Sort: IP",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="pools_sort_key",
            ),
            sg.Button(
                "Hashrate: 0 TH/s",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="pools_total_hashrate",
            ),
            sg.Button(
                "Miners: 0",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="pools_miner_count",
            ),
        ],
        [
            sg.TabGroup(
                [
                    [
                        sg.Tab(
                            "All",
                            [
                                [
                                    sg.Table(
                                        values=[],
                                        headings=[
                                            heading
                                            for heading in TABLE_HEADERS["POOLS_ALL"]
                                        ],
                                        auto_size_columns=False,
                                        max_col_width=15,
                                        justification="center",
                                        key="pools_table",
                                        background_color=POOLS_TABLE_BG,
                                        text_color=POOLS_TABLE_TEXT,
                                        header_background_color=POOLS_TABLE_HEADERS_COLOR,
                                        header_text_color=POOLS_TABLE_HEADERS_TEXT_COLOR,
                                        border_width=POOLS_TABLE_BORDER,
                                        header_border_width=POOLS_TABLE_HEADER_BORDER,
                                        col_widths=col_widths,
                                        size=(0, TABLE_HEIGHT),
                                        expand_x=True,
                                        enable_click_events=True,
                                    )
                                ]
                            ],
                            background_color=POOLS_TABS_BG,
                        )
                    ],
                    [
                        sg.Tab(
                            "Pool 1",
                            [
                                [
                                    sg.Table(
                                        values=[],
                                        headings=[
                                            heading
                                            for heading in TABLE_HEADERS["POOLS_1"]
                                        ],
                                        auto_size_columns=False,
                                        max_col_width=15,
                                        justification="center",
                                        key="pools_1_table",
                                        background_color=POOLS_TABLE_BG,
                                        text_color=POOLS_TABLE_TEXT,
                                        header_background_color=POOLS_TABLE_HEADERS_COLOR,
                                        header_text_color=POOLS_TABLE_HEADERS_TEXT_COLOR,
                                        border_width=POOLS_TABLE_BORDER,
                                        header_border_width=POOLS_TABLE_HEADER_BORDER,
                                        col_widths=col_widths,
                                        size=(0, TABLE_HEIGHT),
                                        expand_x=True,
                                        enable_click_events=True,
                                    )
                                ]
                            ],
                            background_color=POOLS_TABS_BG,
                        )
                    ],
                    [
                        sg.Tab(
                            "Pool 2",
                            [
                                [
                                    sg.Table(
                                        values=[],
                                        headings=[
                                            heading
                                            for heading in TABLE_HEADERS["POOLS_2"]
                                        ],
                                        auto_size_columns=False,
                                        max_col_width=15,
                                        justification="center",
                                        key="pools_2_table",
                                        background_color=POOLS_TABLE_BG,
                                        text_color=POOLS_TABLE_TEXT,
                                        header_background_color=POOLS_TABLE_HEADERS_COLOR,
                                        header_text_color=POOLS_TABLE_HEADERS_TEXT_COLOR,
                                        border_width=POOLS_TABLE_BORDER,
                                        header_border_width=POOLS_TABLE_HEADER_BORDER,
                                        col_widths=col_widths,
                                        size=(0, TABLE_HEIGHT),
                                        expand_x=True,
                                        enable_click_events=True,
                                    )
                                ]
                            ],
                            background_color=POOLS_TABS_BG,
                        )
                    ],
                ],
                background_color=MAIN_TABS_BG,
                title_color=POOLS_TABS_TEXT_NORMAL,
                tab_background_color=POOLS_TABS_NORMAL,
                selected_background_color=POOLS_TABS_SELECTED,
                selected_title_color=POOLS_TABS_TEXT_SELECTED,
                border_width=0,
                tab_border_width=2,
            )
        ],
    ]
    return pools_layout


def get_config_layout():
    config_layout = [
        [
            sg.Button(
                "IMPORT",
                key="cfg_import",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "CONFIG",
                key="cfg_config",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "GENERATE",
                key="cfg_generate",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Push(background_color=MAIN_TABS_BG),
            sg.Button(
                "Sort: IP",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="cfg_sort_key",
            ),
            sg.Button(
                "Hashrate: 0 TH/s",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="cfg_total_hashrate",
            ),
            sg.Button(
                "Miners: 0",
                disabled=True,
                button_color=("black", "white smoke"),
                disabled_button_color=("black", "white smoke"),
                key="cfg_miner_count",
            ),
        ],
        [
            sg.Button(
                "ALL",
                key="cfg_all",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Button(
                "OPEN IN WEB",
                key="cfg_web",
                border_width=BTN_BORDER,
                disabled_button_color=BTN_DISABLED,
            ),
            sg.Push(background_color=MAIN_TABS_BG),
            sg.Checkbox(
                "Append IP to Username",
                key="cfg_append_ip",
                background_color=MAIN_TABS_BG,
            ),
        ],
        [
            sg.Table(
                values=[],
                headings=[heading for heading in TABLE_HEADERS["CONFIG"]],
                auto_size_columns=False,
                max_col_width=15,
                justification="center",
                key="cfg_table",
                background_color=TABLE_BG,
                text_color=TABLE_TEXT,
                header_background_color=TABLE_HEADERS_COLOR,
                header_text_color=TABLE_HEADERS_TEXT_COLOR,
                header_border_width=TABLE_HEADER_BORDER,
                border_width=TABLE_BORDER,
                col_widths=[
                    IP_COL_WIDTH,
                    MODEL_COL_WIDTH,
                    TABLE_TOTAL_WIDTH - ((2 * 40) - 4),
                ],
                size=(0, TABLE_HEIGHT),
                expand_x=True,
                enable_click_events=True,
            ),
            sg.Multiline(size=(40, TABLE_HEIGHT + 1), key="cfg_config_txt"),
        ],
    ]
    return config_layout


layout = [
    [
        sg.Text("", size=(20, 1), key="status"),
        sg.ProgressBar(
            max_value=100, size_px=(0, 20), expand_x=True, key="progress_bar"
        ),
        sg.Text("", size=(20, 1), key="progress_percent", justification="r"),
    ],
    [
        sg.TabGroup(
            [
                [sg.Tab("Scan", get_scan_layout(), background_color=MAIN_TABS_BG)],
                [sg.Tab("Pools", get_pools_layout(), background_color=MAIN_TABS_BG)],
                [
                    sg.Tab(
                        "Configure", get_config_layout(), background_color=MAIN_TABS_BG
                    )
                ],
                [
                    sg.Tab(
                        "Command", get_command_layout(), background_color=MAIN_TABS_BG
                    )
                ],
            ],
            tab_background_color=MAIN_TABS_NORMAL,
            title_color=MAIN_TABS_TEXT_NORMAL,
            selected_background_color=MAIN_TABS_BG,
            selected_title_color=MAIN_TABS_TEXT_SELECTED,
            border_width=0,
            tab_border_width=2,
        ),
    ],
]

window = sg.Window("Upstream Config Util", layout, icon=WINDOW_ICON)
