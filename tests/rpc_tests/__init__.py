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
import json
import time
import unittest
from unittest.mock import patch

from pyasic import APIError
from pyasic.rpc.bfgminer import BFGMinerRPCAPI
from pyasic.rpc.bmminer import BMMinerRPCAPI
from pyasic.rpc.bosminer import BOSMinerRPCAPI
from pyasic.rpc.btminer import BTMinerRPCAPI
from pyasic.rpc.cgminer import CGMinerRPCAPI
from pyasic.rpc.luxminer import LUXMinerRPCAPI


class TestAPIBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ip = "10.0.0.50"
        self.port = 4028
        self.api_str = ""
        self.api = None
        self.setUpData()

    def setUpData(self):
        pass

    def get_error_value(self):
        return json.dumps(
            {
                "STATUS": [
                    {"STATUS": "E", "When": time.time(), "Code": 7, "Msg": self.api_str}
                ],
                "id": 1,
            }
        ).encode("utf-8")

    def get_success_value(self, command: str):
        if self.api_str == "BTMiner" and command == "status":
            return json.dumps(
                {
                    "STATUS": "S",
                    "When": 1706287567,
                    "Code": 131,
                    "Msg": {
                        "mineroff": "false",
                        "mineroff_reason": "",
                        "mineroff_time": "",
                        "FirmwareVersion": "20230911.12.Rel",
                        "power_mode": "",
                        "hash_percent": "",
                    },
                    "Description": "",
                }
            ).encode("utf-8")
        return json.dumps(
            {
                "STATUS": [
                    {
                        "STATUS": "S",
                        "When": time.time(),
                        "Code": 69,
                        "Msg": f"{self.api_str} {command}",
                    }
                ],
                command.upper(): [{command: "test"}],
                "id": 1,
            }
        ).encode("utf-8")

    @patch("pyasic.rpc.base.BaseMinerRPCAPI._send_bytes")
    async def test_command_error_raises_api_error(self, mock_send_bytes):
        if self.api is None:
            return

        mock_send_bytes.return_value = self.get_error_value()
        with self.assertRaises(APIError):
            await self.api.send_command("summary")

    @patch("pyasic.rpc.base.BaseMinerRPCAPI._send_bytes")
    async def test_command_error_ignored_by_flag(self, mock_send_bytes):
        if self.api is None:
            return

        mock_send_bytes.return_value = self.get_error_value()
        try:
            await self.api.send_command(
                "summary", ignore_errors=True, allow_warning=False
            )
        except APIError:
            self.fail(
                f"Expected ignore_errors flag to ignore error in {self.api_str} API"
            )

    @patch("pyasic.rpc.base.BaseMinerRPCAPI._send_bytes")
    async def test_all_read_command_success(self, mock_send_bytes):
        if self.api is None:
            return

        commands = self.api.commands

        for command in commands:
            with self.subTest(
                msg=f"Test of command success on {self.api_str} API with command={command}",
                command=command,
            ):
                api_func = getattr(self.api, command)
                mock_send_bytes.return_value = self.get_success_value(command)
                try:
                    await api_func()
                except APIError:
                    self.fail(f"Expected successful return from API function {command}")
                except TypeError:
                    continue
                except KeyError:
                    continue


class TestBFGMinerAPI(TestAPIBase):
    def setUpData(self):
        self.api = BFGMinerRPCAPI(self.ip)
        self.api_str = "BFGMiner"


class TestBMMinerAPI(TestAPIBase):
    def setUpData(self):
        self.api = BMMinerRPCAPI(self.ip)
        self.api_str = "BMMiner"


class TestBOSMinerAPI(TestAPIBase):
    def setUpData(self):
        self.api = BOSMinerRPCAPI(self.ip)
        self.api_str = "BOSMiner"


class TestBTMinerAPI(TestAPIBase):
    def setUpData(self):
        self.api = BTMinerRPCAPI(self.ip)
        self.api_str = "BTMiner"


class TestCGMinerAPI(TestAPIBase):
    def setUpData(self):
        self.api = CGMinerRPCAPI(self.ip)
        self.api_str = "CGMiner"


class TestLuxOSAPI(TestAPIBase):
    def setUpData(self):
        self.api = LUXMinerRPCAPI(self.ip)
        self.api_str = "LuxOS"


if __name__ == "__main__":
    unittest.main()
