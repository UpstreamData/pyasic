# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------
from ssl import SSLContext
from typing import Any, Union

import httpx
from httpx import AsyncHTTPTransport

_settings = {  # defaults
    "network_ping_retries": 1,
    "network_ping_timeout": 3,
    "network_scan_semaphore": None,
    "factory_get_retries": 1,
    "factory_get_timeout": 3,
    "get_data_retries": 1,
    "api_function_timeout": 5,
    "antminer_mining_mode_as_str": False,
    "default_whatsminer_rpc_password": "admin",
    "default_innosilicon_web_password": "admin",
    "default_antminer_web_password": "root",
    "default_hammer_web_password": "root",
    "default_volcminer_web_password": "ltc@dog",
    "default_bosminer_web_password": "root",
    "default_vnish_web_password": "admin",
    "default_goldshell_web_password": "123456789",
    "default_auradine_web_password": "admin",
    "default_epic_web_password": "letmein",
    "default_hive_web_password": "root",
    "default_iceriver_web_password": "12345678",
    "default_elphapex_web_password": "root",
    "default_mskminer_web_password": "root",
    "default_antminer_ssh_password": "miner",
    "default_bosminer_ssh_password": "root",
}


ssl_cxt = httpx.create_ssl_context()


# this function returns an AsyncHTTPTransport instance to perform asynchronous HTTP requests
# using those options.
def transport(verify: Union[str, bool, SSLContext] = ssl_cxt):
    return AsyncHTTPTransport(verify=verify)


def get(key: str, other: Any = None) -> Any:
    return _settings.get(key, other)


def update(key: str, val: Any) -> Any:
    _settings[key] = val
