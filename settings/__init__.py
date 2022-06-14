import toml
import os

NETWORK_PING_RETRIES: int = 3
NETWORK_PING_TIMEOUT: int = 5
NETWORK_SCAN_THREADS: int = 300

CFG_UTIL_REBOOT_THREADS: int = 300
CFG_UTIL_CONFIG_THREADS: int = 300

MINER_FACTORY_GET_VERSION_RETRIES: int = 3

WHATSMINER_PWD = "admin"

DEBUG = False

settings_keys = {}

try:
    with open(
        os.path.join(os.path.dirname(__file__), "settings.toml"), "r"
    ) as settings_file:
        settings = toml.loads(settings_file.read())
    settings_keys = settings.keys()
except:
    pass

if "ping_retries" in settings_keys:
    NETWORK_PING_RETRIES: int = settings["ping_retries"]
if "ping_timeout" in settings_keys:
    NETWORK_PING_TIMEOUT: int = settings["ping_timeout"]
if "scan_threads" in settings_keys:
    NETWORK_SCAN_THREADS: int = settings["scan_threads"]

if "reboot_threads" in settings_keys:
    CFG_UTIL_REBOOT_THREADS: int = settings["reboot_threads"]
if "config_threads" in settings_keys:
    CFG_UTIL_CONFIG_THREADS: int = settings["config_threads"]


if "get_version_retries" in settings_keys:
    MINER_FACTORY_GET_VERSION_RETRIES: int = settings["get_version_retries"]


if "whatsminer_pwd" in settings_keys:
    WHATSMINER_PWD: str = settings["whatsminer_pwd"]

if "debug" in settings_keys:
    DEBUG: int = settings["debug"]
