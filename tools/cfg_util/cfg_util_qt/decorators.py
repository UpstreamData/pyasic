from tools.cfg_util.cfg_util_qt.layout import window
from tools.cfg_util.cfg_util_qt.layout import BUTTON_KEYS


def disable_buttons(func):
    # handle the inner function that the decorator is wrapping
    async def inner(*args, **kwargs):
        # disable the buttons
        for button in BUTTON_KEYS:
            window[button].Update(disabled=True)

        # call the original wrapped function
        await func(*args, **kwargs)

        # re-enable the buttons after the wrapped function completes
        for button in BUTTON_KEYS:
            window[button].Update(disabled=False)

    return inner
