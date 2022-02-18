from tools.cfg_util.cfg_util_sg.layout import window


def disable_buttons(func):
    button_list = ["scan",
                   "import_file_config",
                   "export_file_config",
                   "import_iplist",
                   "export_iplist",
                   "export_csv",
                   "select_all_ips",
                   "refresh_data",
                   "open_in_web",
                   "reboot_miners",
                   "restart_miner_backend",
                   "import_config",
                   "send_config",
                   "light",
                   "generate_config",
                   ]

    # handle the inner function that the decorator is wrapping
    async def inner(*args, **kwargs):
        # disable the buttons
        for button in button_list:
            window[button].Update(disabled=True)

        # call the original wrapped function
        await func(*args, **kwargs)

        # re-enable the buttons after the wrapped function completes
        for button in button_list:
            window[button].Update(disabled=False)

    return inner
