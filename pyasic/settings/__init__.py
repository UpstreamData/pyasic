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
import socket
import struct
from ssl import SSLContext
from typing import Any, Union

import httpx
from httpx import AsyncHTTPTransport

_settings = {  # defaults
    "network_ping_retries": 1,
    "network_ping_timeout": 3,
    "network_scan_threads": 300,
    "factory_get_retries": 1,
    "factory_get_timeout": 3,
    "get_data_retries": 1,
    "api_function_timeout": 5,
    "default_whatsminer_password": "admin",
    "default_innosilicon_password": "admin",
    "default_antminer_password": "root",
    "default_bosminer_password": "root",
    "default_vnish_password": "admin",
    "default_goldshell_password": "123456789",
    "socket_linger_time": 1000,
}


ssl_cxt = httpx.create_ssl_context()


def transport(verify: Union[str, bool, SSLContext] = ssl_cxt):
    l_onoff = 1
    l_linger = get("so_linger_time", 1000)

    opts = [(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", l_onoff, l_linger))]

    return AsyncHTTPTransport(socket_options=opts, verify=verify)


def get(key: str, other: Any = None) -> Any:
    return _settings.get(key, other)


def update(key: str, val: Any) -> Any:
    _settings[key] = val
