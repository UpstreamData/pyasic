#  Copyright 2022 Upstream Data Inc
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from dataclasses import dataclass

from pyasic.misc import Singleton


@dataclass
class PyasicSettings(metaclass=Singleton):
    network_ping_retries: int = 1
    network_ping_timeout: int = 3
    network_scan_threads: int = 300

    miner_factory_get_version_retries: int = 1

    miner_get_data_retries: int = 1

    global_whatsminer_password = "admin"
    global_innosilicon_password = "admin"
    global_x19_password = "root"
    global_x17_password = "root"

    debug: bool = False
    logfile: bool = False
