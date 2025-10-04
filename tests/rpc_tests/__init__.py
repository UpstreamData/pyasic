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
from unittest.mock import MagicMock, patch

from pyasic import APIError
from pyasic.rpc.bfgminer import BFGMinerRPCAPI
from pyasic.rpc.bmminer import BMMinerRPCAPI
from pyasic.rpc.bosminer import BOSMinerRPCAPI
from pyasic.rpc.btminer import BTMinerRPCAPI
from pyasic.rpc.cgminer import CGMinerRPCAPI
from pyasic.rpc.gcminer import GCMinerRPCAPI
from pyasic.rpc.luxminer import LUXMinerRPCAPI

__all__ = [
    "TestAPIBase",
    "TestBFGMinerAPI",
    "TestBMMinerAPI",
    "TestBOSMinerAPI",
    "TestBTMinerAPI",
    "TestCGMinerAPI",
    "TestGCMinerRPCAPI",
    "TestLuxOSAPI",
]


class TestAPIBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.ip = "10.0.0.50"
        self.port = 4028
        self.api_str = ""
        self.api: (
            BFGMinerRPCAPI
            | BMMinerRPCAPI
            | BOSMinerRPCAPI
            | BTMinerRPCAPI
            | CGMinerRPCAPI
            | GCMinerRPCAPI
            | LUXMinerRPCAPI
            | None
        ) = None
        self.setUpData()

    def setUpData(self) -> None:
        pass

    def get_error_value(self) -> bytes:
        return json.dumps(
            {
                "STATUS": [
                    {"STATUS": "E", "When": time.time(), "Code": 7, "Msg": self.api_str}
                ],
                "id": 1,
            }
        ).encode("utf-8")

    def get_success_value(self, command: str) -> bytes:
        if self.api_str == "BTMiner":
            if command == "status":
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
            elif command == "get_token":
                # Return proper token response for BTMiner matching real miner format
                return json.dumps(
                    {
                        "STATUS": "S",
                        "When": int(time.time()),
                        "Code": 134,
                        "Msg": {
                            "time": str(int(time.time())),
                            "salt": "D6w5gVOb",  # Valid salt format (alphanumeric only)
                            "newsalt": "zU4gvW30",  # Valid salt format (alphanumeric only)
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
    async def test_command_error_raises_api_error(
        self, mock_send_bytes: MagicMock
    ) -> None:
        if self.api is None:
            return

        mock_send_bytes.return_value = self.get_error_value()
        with self.assertRaises(APIError):
            await self.api.send_command("summary")

    @patch("pyasic.rpc.base.BaseMinerRPCAPI._send_bytes")
    async def test_command_error_ignored_by_flag(
        self, mock_send_bytes: MagicMock
    ) -> None:
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
    async def test_all_read_command_success(self, mock_send_bytes: MagicMock) -> None:
        if self.api is None:
            return

        commands = self.api.commands

        for command in commands:
            with self.subTest(
                msg=f"Test of command success on {self.api_str} API with command={command}",
                command=command,
            ):
                api_func = getattr(self.api, command)

                # For BTMiner, we need to handle multiple calls for privileged commands
                # Use a list to track calls and return different values
                if self.api_str == "BTMiner":

                    def btminer_side_effect(data: bytes) -> bytes:
                        # Parse the command from the sent data
                        try:
                            # data is already bytes
                            if isinstance(data, bytes):
                                cmd_str = data.decode("utf-8")
                                cmd_data = json.loads(cmd_str)
                                if "cmd" in cmd_data:
                                    sent_cmd = cmd_data["cmd"]
                                    if sent_cmd == "get_token":
                                        # Return proper token response
                                        return self.get_success_value("get_token")
                        except Exception:
                            # If we can't parse it, it might be encrypted privileged command
                            pass
                        # Default return for the actual command
                        return self.get_success_value(command)

                    mock_send_bytes.side_effect = btminer_side_effect
                else:
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
    def setUpData(self) -> None:
        self.api: BFGMinerRPCAPI = BFGMinerRPCAPI(self.ip)
        self.api_str = "BFGMiner"


class TestBMMinerAPI(TestAPIBase):
    def setUpData(self) -> None:
        self.api: BMMinerRPCAPI = BMMinerRPCAPI(self.ip)
        self.api_str = "BMMiner"


class TestBOSMinerAPI(TestAPIBase):
    def setUpData(self) -> None:
        self.api: BOSMinerRPCAPI = BOSMinerRPCAPI(self.ip)
        self.api_str = "BOSMiner"


class TestBTMinerAPI(TestAPIBase):
    def setUpData(self) -> None:
        self.api: BTMinerRPCAPI = BTMinerRPCAPI(self.ip)
        self.api_str = "BTMiner"


class TestCGMinerAPI(TestAPIBase):
    def setUpData(self) -> None:
        self.api: CGMinerRPCAPI = CGMinerRPCAPI(self.ip)
        self.api_str = "CGMiner"


class TestGCMinerRPCAPI(TestAPIBase):
    def setUpData(self) -> None:
        self.api: GCMinerRPCAPI = GCMinerRPCAPI(self.ip)
        self.api_str = "GCMiner"


class TestLuxOSAPI(TestAPIBase):
    def setUpData(self) -> None:
        self.api: LUXMinerRPCAPI = LUXMinerRPCAPI(self.ip)
        self.api_str = "LuxOS"


if __name__ == "__main__":
    unittest.main()
