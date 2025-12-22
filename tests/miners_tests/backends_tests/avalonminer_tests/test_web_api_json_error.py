"""Tests for AvalonMiner web API JSON error handling.

This test ensures that the AvalonMiner API gracefully handles
cases where endpoints return invalid JSON or HTML responses
instead of the expected JSON data.

Related to Issue #400: Avalon Mini 3 stopped working with v0.78.0
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from pyasic.miners.avalonminer.cgminer.mini.mini3 import CGMinerAvalonMini3
from pyasic.miners.avalonminer.cgminer.nano.nano3 import CGMinerAvalonNano3
from pyasic.web.avalonminer import AvalonMinerWebAPI


class TestAvalonMinerWebAPIJsonErrors(unittest.IsolatedAsyncioTestCase):
    """Test AvalonMiner web API exception handling for JSON decode errors."""

    async def test_send_command_json_decode_error(self):
        """Test that send_command handles JSON decode errors gracefully.

        When a CGI endpoint returns invalid JSON (e.g., HTML error page),
        the send_command method should return an empty dict instead of
        raising an exception.
        """
        api = AvalonMinerWebAPI("192.168.1.100")

        with patch("pyasic.web.avalonminer.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            # Simulate invalid JSON response (e.g., HTML error page)
            mock_response.text = "<html><body>Error</body></html>"

            mock_client.get.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await api.send_command("get_minerinfo")

            # Should return empty dict instead of raising JSONDecodeError
            self.assertEqual(result, {})

    async def test_send_command_http_error(self):
        """Test that send_command handles HTTP errors gracefully.

        When an HTTP error occurs, send_command should return an empty dict
        instead of raising an exception.
        """
        api = AvalonMinerWebAPI("192.168.1.100")

        with patch("pyasic.web.avalonminer.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.HTTPError("Connection failed")

            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await api.send_command("get_minerinfo")

            # Should return empty dict instead of raising HTTPError
            self.assertEqual(result, {})

    async def test_multicommand_json_decode_error(self):
        """Test that multicommand handles JSON decode errors gracefully.

        This is the critical fix for issue #400. When a CGI endpoint
        returns invalid JSON (e.g., HTML error page), the multicommand
        method should skip that command and continue with others.
        """
        api = AvalonMinerWebAPI("192.168.1.100")

        with patch("pyasic.web.avalonminer.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.cookies = MagicMock()

            async def mock_get(url):
                response = MagicMock()
                # One endpoint returns valid JSON, another returns invalid HTML
                if "minerinfo" in url:
                    response.text = "<html><body>Error</body></html>"
                else:
                    response.text = '{"status": "ok"}'
                return response

            mock_client.get = mock_get
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            # Call multicommand with multiple endpoints
            result = await api.multicommand("get_minerinfo", "get_home")

            # Should return data from successful commands and empty dict for failed ones
            self.assertIn("status", result)
            self.assertEqual(result["status"], "ok")
            self.assertIn("multicommand", result)
            self.assertTrue(result["multicommand"])

    async def test_multicommand_fallback_get_miner_info(self):
        """Test multicommand falls back from get_minerinfo to get_miner_info."""

        api = AvalonMinerWebAPI("192.168.1.100")

        with patch("pyasic.web.avalonminer.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.cookies = MagicMock()

            async def mock_get(url):
                response = MagicMock()
                if "get_minerinfo" in url:
                    response.text = "<html><body>Error</body></html>"
                elif "get_miner_info" in url:
                    response.text = '{"status": "ok", "mac": "aa:bb"}'
                else:
                    response.text = "{}"
                return response

            mock_client.get = mock_get
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await api.multicommand("get_minerinfo")

            self.assertIn("status", result)
            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["multicommand"])

    async def test_multicommand_fallback_status(self):
        """Test multicommand falls back from get_status to status."""

        api = AvalonMinerWebAPI("192.168.1.100")

        with patch("pyasic.web.avalonminer.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.cookies = MagicMock()

            async def mock_get(url):
                response = MagicMock()
                if "get_status" in url:
                    response.text = "<html><body>Error</body></html>"
                elif "status" in url:
                    response.text = '{"status": "ok", "temp": 42}'
                else:
                    response.text = "{}"
                return response

            mock_client.get = mock_get
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await api.multicommand("get_status")

            self.assertIn("status", result)
            self.assertEqual(result["status"], "ok")
            self.assertTrue(result["multicommand"])

    async def test_minerinfo_method_fallback(self):
        """Test minerinfo() tries get_minerinfo then get_miner_info."""

        api = AvalonMinerWebAPI("192.168.1.100")

        with patch.object(api, "send_command", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = [
                {},
                {"mac": "de:ad:be:ef:00:01"},
            ]

            result = await api.minerinfo()

            self.assertEqual(result.get("mac"), "de:ad:be:ef:00:01")
            self.assertEqual(mock_send.await_count, 2)

    async def test_status_method_fallback(self):
        """Test status() tries get_status then status."""

        api = AvalonMinerWebAPI("192.168.1.100")

        with patch.object(api, "send_command", new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = [
                {},
                {"temp": 42, "status": "ok"},
            ]

            result = await api.status()

            self.assertEqual(result.get("temp"), 42)
            self.assertEqual(mock_send.await_count, 2)

    async def test_multicommand_all_failures(self):
        """Test multicommand when all endpoints fail.

        When all CGI endpoints return invalid JSON, the multicommand
        should return a dict with only the multicommand flag set to True.
        """
        api = AvalonMinerWebAPI("192.168.1.100")

        with patch("pyasic.web.avalonminer.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.cookies = MagicMock()

            async def mock_get(url):
                response = MagicMock()
                # All endpoints return invalid HTML
                response.text = "<html><body>404 Not Found</body></html>"
                return response

            mock_client.get = mock_get
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            # Call multicommand with multiple endpoints
            result = await api.multicommand(
                "get_minerinfo", "get_home", "nonexistent_endpoint"
            )

            # Should return a dict with only multicommand=True
            self.assertEqual(result, {"multicommand": True})

    async def test_mini3_mac_address_fallback(self):
        """Test that Mini3 can fetch MAC address using get_miner_info with fallback.

        The Mini3 attempts to use get_miner_info first, then falls back to
        get_minerinfo if the first fails. This test ensures both methods work.
        """
        miner = CGMinerAvalonMini3("192.168.1.100")

        with patch.object(
            miner.web, "miner_info", new_callable=AsyncMock
        ) as mock_miner_info:
            # Simulate successful response from get_miner_info
            mock_miner_info.return_value = {"mac": "00:11:22:33:44:55"}

            result = await miner._get_mac()

            self.assertEqual(result, "00:11:22:33:44:55")
            mock_miner_info.assert_called_once()

    async def test_mini3_mac_address_fallback_failure(self):
        """Test that Mini3 falls back from get_miner_info to get_minerinfo.

        When get_miner_info (with underscore) fails, the _get_mac method
        should fall back to get_minerinfo. This test ensures both endpoints
        are tried before giving up.
        """
        from pyasic import APIError

        miner = CGMinerAvalonMini3("192.168.1.100")

        with (
            patch.object(
                miner.web, "miner_info", new_callable=AsyncMock
            ) as mock_miner_info,
            patch.object(
                miner.web, "minerinfo", new_callable=AsyncMock
            ) as mock_minerinfo,
        ):
            # Simulate get_miner_info failing but minerinfo succeeding
            mock_miner_info.side_effect = APIError("Not found")
            mock_minerinfo.return_value = {"mac": "aa:bb:cc:dd:ee:ff"}

            result = await miner._get_mac()

            self.assertEqual(result, "AA:BB:CC:DD:EE:FF")
            mock_miner_info.assert_called_once()
            mock_minerinfo.assert_called_once()

    async def test_mini3_mac_address_both_fail(self):
        """Test that Mini3 returns None when all endpoints fail.

        When both get_miner_info and get_minerinfo fail, the _get_mac
        method should gracefully return None.
        """
        from pyasic import APIError

        miner = CGMinerAvalonMini3("192.168.1.100")

        with (
            patch.object(
                miner.web, "miner_info", new_callable=AsyncMock
            ) as mock_miner_info,
            patch.object(
                miner.web, "minerinfo", new_callable=AsyncMock
            ) as mock_minerinfo,
        ):
            # Simulate both endpoints failing
            mock_miner_info.side_effect = APIError("Not found")
            mock_minerinfo.side_effect = APIError("Connection failed")

            result = await miner._get_mac()

            self.assertIsNone(result)

    async def test_nano3_mac_address_fallback(self):
        """Test that Nano3 can fetch MAC address using get_miner_info with fallback.

        Similar to Mini3, Nano3 data locations do not include the
        get_minerinfo command, so fallback to get_miner_info is required.
        """
        miner = CGMinerAvalonNano3("192.168.1.100")

        with patch.object(
            miner.web, "miner_info", new_callable=AsyncMock
        ) as mock_miner_info:
            # Simulate successful response from get_miner_info
            mock_miner_info.return_value = {"mac": "aa:bb:cc:dd:ee:ff"}

            result = await miner._get_mac()

            self.assertEqual(result, "AA:BB:CC:DD:EE:FF")
            mock_miner_info.assert_called_once()


if __name__ == "__main__":
    unittest.main()
