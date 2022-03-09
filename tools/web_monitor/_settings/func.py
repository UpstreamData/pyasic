import toml
import os


def get_current_settings():
    try:
        with open(os.path.join(os.getcwd(), "settings/web_settings.toml"), "r") as settings_file:
            settings = toml.loads(settings_file.read())
    except:
        settings = {
            "graph_data_sleep_time": 1,
            "miner_data_timeout": 5,
            "miner_identify_timeout": 5,
        }
    return settings


def update_settings(settings):
    with open(os.path.join(os.getcwd(), "settings/web_settings.toml"), "w") as settings_file:
        settings_file.write(toml.dumps(settings))
