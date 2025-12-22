"""Tests for AvalonMiner web API JSON error handling.

This test ensures that the AvalonMiner API gracefully handles
cases where endpoints return invalid JSON or HTML responses
instead of the expected JSON data.

Related to Issue #400: Avalon Mini 3 stopped working with v0.78.0
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

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


if __name__ == "__main__":
    unittest.main()
