import toml
import os

# noinspection PyPep8
try:
    with open(os.path.join(os.getcwd(), "settings.toml"), "r") as settings_file:
        settings = toml.loads(settings_file.read())
    NETWORK_PING_RETRIES: int = settings["ping_retries"]
    NETWORK_PING_TIMEOUT: int = settings["ping_timeout"]
    NETWORK_SCAN_THREADS: int = settings["scan_threads"]

    CFG_UTIL_CONFIG_THREADS: int = settings["config_threads"]

    MINER_FACTORY_GET_VERSION_RETRIES: int = settings["get_version_retries"]
except:
    NETWORK_PING_RETRIES: int = 3
    NETWORK_PING_TIMEOUT: int = 5
    NETWORK_SCAN_THREADS: int = 300

    CFG_UTIL_CONFIG_THREADS: int = 300

    MINER_FACTORY_GET_VERSION_RETRIES: int = 3
