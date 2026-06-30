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
bosminer_api_pools = {
    "STATUS": [
        {
            "STATUS": "S",
            "Msg": "2 Pool(s)",
            "Description": "",
        }
    ],
    "POOLS": [
        {
            "POOL": 0,
            "URL": "stratum+tcp://pyasic.testpool_1.pool:3333",
            "Status": "Alive",
            "Quota": 1,
            "User": "pyasic.test",
            "Stratum URL": "pyasic.testpool_1.pool:3333",
            "AsicBoost": True,
        },
        {
            "POOL": 1,
            "URL": "stratum+tcp://pyasic.testpool_2.pool:3333",
            "Status": "Alive",
            "Quota": 1,
            "User": "pyasic.test",
            "Stratum URL": "pyasic.testpool_2.pool:3333",
            "AsicBoost": True,
        },
    ],
    "id": 1,
}

x19_api_pools = {
    "STATUS": [
        {
            "STATUS": "S",
            "Msg": "2 Pool(s)",
            "Description": "",
        }
    ],
    "POOLS": [
        {
            "POOL": 0,
            "URL": "stratum+tcp://pyasic.testpool_1.pool:3333",
            "Status": "Alive",
            "Quota": 1,
            "User": "pyasic.test",
            "Stratum URL": "pyasic.testpool_1.pool:3333",
        },
        {
            "POOL": 1,
            "URL": "stratum+tcp://pyasic.testpool_2.pool:3333",
            "Status": "Alive",
            "Quota": 1,
            "User": "pyasic.test",
            "Stratum URL": "pyasic.testpool_2.pool:3333",
        },
    ],
    "id": 1,
}

x19_web_pools = {
    "pools": [
        {
            "url": "stratum+tcp://pyasic.testpool_1.pool:3333",
            "user": "pyasic.test",
            "pass": "123",
        },
        {
            "url": "stratum+tcp://pyasic.testpool_2.pool:3333",
            "user": "pyasic.test",
            "pass": "123",
        },
    ],
    "api-listen": True,
    "api-network": True,
    "api-groups": "A:stats:pools:devs:summary:version",
    "api-allow": "A:0/0,W:*",
    "bitmain-fan-ctrl": False,
    "bitmain-fan-pwm": "100",
    "bitmain-use-vil": True,
    "bitmain-freq": "675",
    "bitmain-voltage": "1400",
    "bitmain-ccdelay": "0",
    "bitmain-pwth": "0",
    "bitmain-work-mode": "0",
    "bitmain-freq-level": "100",
}

bosminer_config_pools = {
    "format": {
        "version": "1.2+",
        "model": "Antminer S9",
        "generator": "pyasic",
    },
    "group": [
        {
            "name": "TEST",
            "quota": 1,
            "pool": [
                {
                    "enabled": True,
                    "url": "stratum+tcp://pyasic.testpool_1.pool:3333",
                    "user": "pyasic.test",
                    "password": "123",
                },
                {
                    "enabled": True,
                    "url": "stratum+tcp://pyasic.testpool_2.pool:3333",
                    "user": "pyasic.test",
                    "password": "123",
                },
            ],
        },
    ],
}
