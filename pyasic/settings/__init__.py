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
from typing import Any

import httpx
from httpx import AsyncHTTPTransport
from pydantic import BaseModel, Field


class Settings(BaseModel):
    network_ping_retries: int = Field(default=1)
    network_ping_timeout: int = Field(default=3)
    network_scan_semaphore: int | None = Field(default=None)
    factory_get_retries: int = Field(default=1)
    factory_get_timeout: int = Field(default=3)
    get_data_retries: int = Field(default=1)
    api_function_timeout: int = Field(default=5)
    antminer_mining_mode_as_str: bool = Field(default=False)
    default_whatsminer_rpc_password: str = Field(default="admin")
    default_innosilicon_web_password: str = Field(default="admin")
    default_antminer_web_password: str = Field(default="root")
    default_hammer_web_password: str = Field(default="root")
    default_volcminer_web_password: str = Field(default="ltc@dog")
    default_bosminer_web_password: str = Field(default="root")
    default_vnish_web_password: str = Field(default="admin")
    default_goldshell_web_password: str = Field(default="123456789")
    default_auradine_web_password: str = Field(default="admin")
    default_epic_web_password: str = Field(default="letmein")
    default_hive_web_password: str = Field(default="root")
    default_iceriver_web_password: str = Field(default="12345678")
    default_elphapex_web_password: str = Field(default="root")
    default_mskminer_web_password: str = Field(default="root")
    default_antminer_ssh_password: str = Field(default="miner")
    default_bosminer_ssh_password: str = Field(default="root")

    class Config:
        validate_assignment = True
        extra = "allow"


_settings = Settings()


ssl_cxt = httpx.create_ssl_context()


# this function returns an AsyncHTTPTransport instance to perform asynchronous HTTP requests
# using those options.
def transport(verify: str | bool | SSLContext = ssl_cxt):
    return AsyncHTTPTransport(verify=verify)


def get(key: str, other: Any = None) -> Any:
    try:
        return getattr(_settings, key)
    except AttributeError:
        if hasattr(_settings, "__dict__") and key in _settings.__dict__:
            return _settings.__dict__[key]
        return other


def update(key: str, val: Any) -> None:
    if hasattr(_settings, key):
        setattr(_settings, key, val)
    else:
        _settings.__dict__[key] = val
