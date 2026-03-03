"""Tests for Antminer stock firmware password change."""

import unittest
from unittest.mock import AsyncMock, patch

from pyasic.web.antminer import AntminerModernWebAPI


class TestAntminerModernChangePassword(unittest.IsolatedAsyncioTestCase):
    """Test AntminerModernWebAPI.change_password and the AntminerModern backend."""

    async def test_web_api_success_updates_stored_password(self):
        """Successful passwd.cgi response updates self.pwd."""
        # Arrange
        api = AntminerModernWebAPI("192.168.1.1")
        api.pwd = "old_password"  # nosec B105 - test fixture

        with patch.object(api, "send_command", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {
                "stats": "success",
                "code": "M000",
                "msg": "",
            }

            # Act
            result = await api.change_password("new_password")

            # Assert
            mock_send.assert_awaited_once_with(
                "passwd",
                curPwd="old_password",
                newPwd="new_password",
                confirmPwd="new_password",
            )
            self.assertEqual(result["stats"], "success")
            self.assertEqual(api.pwd, "new_password")

    async def test_web_api_failure_preserves_stored_password(self):
        """Failed passwd.cgi response leaves self.pwd unchanged."""
        # Arrange
        api = AntminerModernWebAPI("192.168.1.1")
        api.pwd = "old_password"  # nosec B105 - test fixture

        with patch.object(api, "send_command", new_callable=AsyncMock) as mock_send:
            mock_send.return_value = {
                "stats": "error",
                "code": "E000",
                "msg": "wrong password",
            }

            # Act
            result = await api.change_password("new_password")

            # Assert
            self.assertEqual(result["stats"], "error")
            self.assertEqual(api.pwd, "old_password")

    async def test_backend_returns_true_on_success(self):
        """AntminerModern.change_password returns True when the API succeeds."""
        from pyasic.miners.backends.antminer import AntminerModern

        # Arrange
        miner = AntminerModern("192.168.1.1")

        with patch.object(
            miner.web, "change_password", new_callable=AsyncMock
        ) as mock_change:
            mock_change.return_value = {"stats": "success", "code": "M000", "msg": ""}

            # Act
            result = await miner.change_password("new_password")

            # Assert
            self.assertTrue(result)
            mock_change.assert_awaited_once_with("new_password")

    async def test_backend_returns_false_on_failure(self):
        """AntminerModern.change_password returns False when the API fails."""
        from pyasic.miners.backends.antminer import AntminerModern

        # Arrange
        miner = AntminerModern("192.168.1.1")

        with patch.object(
            miner.web, "change_password", new_callable=AsyncMock
        ) as mock_change:
            mock_change.return_value = {
                "stats": "error",
                "code": "E000",
                "msg": "wrong password",
            }

            # Act
            result = await miner.change_password("new_password")

            # Assert
            self.assertFalse(result)

    async def test_base_miner_default_returns_false(self):
        """BaseMiner.change_password returns False by default."""
        from pyasic.miners.base import BaseMiner

        # Act
        result = await BaseMiner.change_password(BaseMiner, "anything")

        # Assert
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
