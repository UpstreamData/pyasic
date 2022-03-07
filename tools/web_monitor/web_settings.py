import toml
import os

try:
    with open(os.path.join(os.getcwd(), "web_settings.toml"), "r") as settings_file:
        settings = toml.loads(settings_file.read())
    GRAPH_SLEEP_TIME: int = settings["graph_data_sleep_time"]
    MINER_DATA_TIMEOUT: int = settings["miner_data_timeout"]
    MINER_IDENTIFY_TIMEOUT: int = settings["miner_identify_timeout"]
except:
    GRAPH_SLEEP_TIME: int = 1
    MINER_DATA_TIMEOUT: int = 5
    MINER_IDENTIFY_TIMEOUT: int = 5
