from tools.bad_board_util.layout import window


def disable_buttons(func):
    button_list = [
        "scan",
        "import_iplist",
        "export_iplist",
        "select_all_ips",
        "refresh_data",
        "open_in_web",
        "save_report_button",
        "light",
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
