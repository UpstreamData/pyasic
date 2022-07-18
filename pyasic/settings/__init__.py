from dataclasses import dataclass


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


@dataclass
class PyasicSettings(metaclass=Singleton):
    network_ping_retries: int = 3
    network_ping_timeout: int = 5
    network_scan_threads: int = 300

    miner_factory_get_version_retries: int = 1

    miner_get_data_retries: int = 1

    global_whatsminer_password = "admin"

    debug: bool = False
    logfile: bool = False
