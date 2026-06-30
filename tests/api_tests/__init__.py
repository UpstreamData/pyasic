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
import asyncio
import unittest
from unittest.mock import MagicMock, Mock, patch

from pyasic.API.bmminer import BMMinerAPI
from pyasic.API.bosminer import BOSMinerAPI
from pyasic.API.btminer import BTMinerAPI
from pyasic.API.cgminer import CGMinerAPI


class TestBMMinerAPI(unittest.IsolatedAsyncioTestCase):
    async def create_mock_connection(self, reader_data: bytes = b""):
        mock_reader = Mock(asyncio.StreamReader)
        mock_reader.read.side_effect = [reader_data, None]
        mock_writer = Mock(asyncio.StreamWriter)
        mock_writer.write.return_value = None
        mock_writer.drain.return_value = None
        mock_writer.get_extra_info.return_value = (self.ip, self.port)
        mock_connection = MagicMock()
        mock_connection.__aenter__.return_value = (mock_reader, mock_writer)
        mock_connection.__aexit__.return_value = None
        return mock_connection

    def setUp(self):
        self.ip = "192.168.0.1"
        self.port = 4028

    @patch("pyasic.API.BaseMinerAPI._send_bytes")
    async def test_send_command(self, mock_send_bytes):
        miner_api = BMMinerAPI(ip=self.ip, port=self.port)
        mock_send_bytes.return_value = b'{"STATUS":[{"STATUS":"S","When":1618486231,"Code":7,"Msg":"BMMiner"}], "SUMMARY":[{}], "id": 1}'
        response = await miner_api.send_command("summary")
        self.assertIsInstance(response, dict)
        self.assertEqual(response["STATUS"][0]["STATUS"], "S")

    @patch("pyasic.API.BaseMinerAPI._send_bytes")
    async def test_all_commands(self, mock_send_bytes):
        miner_api = BMMinerAPI(ip=self.ip, port=self.port)
        for command in miner_api.commands:
            mock_send_bytes.return_value = (
                b'{"STATUS":[{"STATUS":"S","When":1618486231,"Code":7,"Msg":"BMMiner"}], "'
                + command.upper().encode("utf-8")
                + b'":[{}], "id": 1}'
            )
            try:
                command_func = getattr(miner_api, command)
            except AttributeError:
                pass
            else:
                try:
                    response = await command_func()
                except TypeError:
                    # probably addpool or something
                    pass
                else:
                    self.assertIsInstance(response, dict)
                    self.assertEqual(response["STATUS"][0]["STATUS"], "S")

    async def test_init(self):
        miner_api = BMMinerAPI(ip=self.ip, port=self.port)
        self.assertEqual(str(miner_api.ip), self.ip)
        self.assertEqual(miner_api.port, self.port)
        self.assertEqual(str(miner_api), "BMMinerAPI: 192.168.0.1")


class TestBTMinerAPI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ip = "192.168.0.1"
        self.port = 4028

    @patch("pyasic.API.BaseMinerAPI._send_bytes")
    async def test_send_command(self, mock_send_bytes):
        mock_send_bytes.return_value = b'{"STATUS":[{"STATUS":"S","When":1618486231,"Code":7,"Msg":"BTMiner"}], "SUMMARY":[{"sumamry": 1}], "id": 1}'
        miner_api = BTMinerAPI(ip=self.ip, port=self.port)
        response = await miner_api.send_command("summary")
        self.assertIsInstance(response, dict)
        self.assertEqual(response["STATUS"][0]["STATUS"], "S")

    @patch("pyasic.API.BaseMinerAPI._send_bytes")
    async def test_all_commands(self, mock_send_bytes):
        miner_api = BMMinerAPI(ip=self.ip, port=self.port)
        for command in miner_api.commands:
            mock_send_bytes.return_value = (
                b'{"STATUS":[{"STATUS":"S","When":1618486231,"Code":7,"Msg":"BTMiner"}], "'
                + command.upper().encode("utf-8")
                + b'":[{}], "id": 1}'
            )
            try:
                command_func = getattr(miner_api, command)
            except AttributeError:
                pass
            else:
                try:
                    response = await command_func()
                except TypeError:
                    # probably addpool or something
                    pass
                else:
                    self.assertIsInstance(response, dict)
                    self.assertEqual(response["STATUS"][0]["STATUS"], "S")

    async def test_init(self):
        miner_api = BTMinerAPI(ip=self.ip, port=self.port)
        self.assertEqual(str(miner_api.ip), self.ip)
        self.assertEqual(miner_api.port, self.port)
        self.assertEqual(str(miner_api), "BTMinerAPI: 192.168.0.1")


class TestCGMinerAPI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ip = "192.168.0.1"
        self.port = 4028

    @patch("pyasic.API.BaseMinerAPI._send_bytes")
    async def test_send_command(self, mock_send_bytes):
        mock_send_bytes.return_value = b'{"STATUS":[{"STATUS":"S","When":1618486231,"Code":7,"Msg":"CGMiner"}], "SUMMARY":[{"sumamry": 1}], "id": 1}'
        miner_api = CGMinerAPI(ip=self.ip, port=self.port)
        response = await miner_api.send_command("summary")
        self.assertIsInstance(response, dict)
        self.assertEqual(response["STATUS"][0]["STATUS"], "S")

    @patch("pyasic.API.BaseMinerAPI._send_bytes")
    async def test_all_commands(self, mock_send_bytes):
        miner_api = BMMinerAPI(ip=self.ip, port=self.port)
        for command in miner_api.commands:
            mock_send_bytes.return_value = (
                b'{"STATUS":[{"STATUS":"S","When":1618486231,"Code":7,"Msg":"CGMiner"}], "'
                + command.upper().encode("utf-8")
                + b'":[{}], "id": 1}'
            )
            try:
                command_func = getattr(miner_api, command)
            except AttributeError:
                pass
            else:
                try:
                    response = await command_func()
                except TypeError:
                    # probably addpool or something
                    pass
                else:
                    self.assertIsInstance(response, dict)
                    self.assertEqual(response["STATUS"][0]["STATUS"], "S")

    async def test_init(self):
        miner_api = CGMinerAPI(ip=self.ip, port=self.port)
        self.assertEqual(str(miner_api.ip), self.ip)
        self.assertEqual(miner_api.port, self.port)
        self.assertEqual(str(miner_api), "CGMinerAPI: 192.168.0.1")


class TestBOSMinerAPI(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.ip = "192.168.0.1"
        self.port = 4028

    @patch("pyasic.API.BaseMinerAPI._send_bytes")
    async def test_send_command(self, mock_send_bytes):
        mock_send_bytes.return_value = b'{"STATUS":[{"STATUS":"S","When":1618486231,"Code":7,"Msg":"BOSMiner"}], "SUMMARY":[{"sumamry": 1}], "id": 1}'
        miner_api = BOSMinerAPI(ip=self.ip, port=self.port)
        response = await miner_api.send_command("summary")
        self.assertIsInstance(response, dict)
        self.assertEqual(response["STATUS"][0]["STATUS"], "S")

    @patch("pyasic.API.BaseMinerAPI._send_bytes")
    async def test_all_commands(self, mock_send_bytes):
        miner_api = BMMinerAPI(ip=self.ip, port=self.port)
        for command in miner_api.commands:
            mock_send_bytes.return_value = (
                b'{"STATUS":[{"STATUS":"S","When":1618486231,"Code":7,"Msg":"BOSMiner"}], "'
                + command.upper().encode("utf-8")
                + b'":[{}], "id": 1}'
            )
            try:
                command_func = getattr(miner_api, command)
            except AttributeError:
                pass
            else:
                try:
                    response = await command_func()
                except TypeError:
                    # probably addpool or something
                    pass
                else:
                    self.assertIsInstance(response, dict)
                    self.assertEqual(response["STATUS"][0]["STATUS"], "S")

    async def test_init(self):
        miner_api = BOSMinerAPI(ip=self.ip, port=self.port)
        self.assertEqual(str(miner_api.ip), self.ip)
        self.assertEqual(miner_api.port, self.port)
        self.assertEqual(str(miner_api), "BOSMinerAPI: 192.168.0.1")


if __name__ == "__main__":
    unittest.main()
