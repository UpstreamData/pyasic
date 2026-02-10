"""Tests for LuxOS set_profile() method."""

import logging
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from pyasic.config.mining import MiningModeConfig
from pyasic.config.mining.presets import MiningPreset


def _make_preset(name, power=1000, frequency=400, voltage=8.9):
    """Helper to create a MiningPreset."""
    return MiningPreset(
        name=name,
        power=power,
        hashrate=80.0,
        tuned=True,
        modded_psu=False,
        frequency=frequency,
        voltage=voltage,
    )


def _make_config(
    active_preset_name="415MHz", available_preset_names=("190MHz", "415MHz", "565MHz")
):
    """Helper to create a mock config with presets."""
    presets = [_make_preset(n) for n in available_preset_names]
    active = next((p for p in presets if p.name == active_preset_name), presets[0])
    config = MagicMock()
    config.mining_mode.available_presets = presets
    config.mining_mode.active_preset = active
    return config


class TestSetProfile(unittest.IsolatedAsyncioTestCase):
    """Test LuxOS set_profile() behavior."""

    def _make_miner(self, atm_enabled=True, config=None, profileset_result=None):
        """Create a mock LuxOS miner with controllable behavior."""
        from pyasic.miners.backends.luxminer import LUXMiner

        miner = LUXMiner.__new__(LUXMiner)
        miner.rpc = MagicMock()
        miner.rpc.atmset = AsyncMock()
        miner.rpc.profileset = AsyncMock(
            return_value=profileset_result or {"PROFILE": [{"Profile": "415MHz"}]}
        )
        miner.atm_enabled = AsyncMock(return_value=atm_enabled)
        miner.get_config = AsyncMock(return_value=config or _make_config())
        miner.ip = "192.168.1.237"
        return miner

    async def test_switches_preset_with_atm_on(self):
        """When ATM is on, should disable ATM, switch, then re-enable ATM."""
        miner = self._make_miner(
            atm_enabled=True,
            profileset_result={"PROFILE": [{"Profile": "190MHz"}]},
        )

        result = await miner.set_profile("190MHz")

        self.assertTrue(result)
        miner.rpc.atmset.assert_any_call(enabled=False)
        miner.rpc.profileset.assert_called_once_with("190MHz")
        miner.rpc.atmset.assert_any_call(enabled=True)

    async def test_switches_preset_with_atm_off(self):
        """When ATM is off, should switch without toggling ATM."""
        miner = self._make_miner(
            atm_enabled=False,
            profileset_result={"PROFILE": [{"Profile": "190MHz"}]},
        )

        result = await miner.set_profile("190MHz")

        self.assertTrue(result)
        miner.rpc.atmset.assert_not_called()
        miner.rpc.profileset.assert_called_once_with("190MHz")

    async def test_invalid_preset_name_returns_false(self):
        """Should return False when preset name doesn't exist."""
        miner = self._make_miner()

        result = await miner.set_profile("nonexistent_profile")

        self.assertFalse(result)
        miner.rpc.profileset.assert_not_called()

    async def test_atm_re_enable_failure_returns_true_and_warns(self):
        """If preset switches but ATM re-enable fails, return True and log warning."""
        miner = self._make_miner(
            atm_enabled=True,
            profileset_result={"PROFILE": [{"Profile": "190MHz"}]},
        )
        # First call (disable) succeeds, second call (re-enable) fails
        miner.rpc.atmset.side_effect = [None, Exception("ATM re-enable failed")]

        with self.assertLogs(level=logging.WARNING):
            result = await miner.set_profile("190MHz")

        self.assertTrue(result)
        miner.rpc.profileset.assert_called_once_with("190MHz")

    async def test_fuzzy_match_case_insensitive(self):
        """Should match preset name case-insensitively."""
        miner = self._make_miner(
            atm_enabled=False,
            profileset_result={"PROFILE": [{"Profile": "190MHz"}]},
        )

        result = await miner.set_profile("190mhz")

        self.assertTrue(result)
        miner.rpc.profileset.assert_called_once_with("190MHz")

    async def test_fuzzy_match_number_only(self):
        """Should match '190' to '190MHz'."""
        miner = self._make_miner(
            atm_enabled=False,
            profileset_result={"PROFILE": [{"Profile": "190MHz"}]},
        )

        result = await miner.set_profile("190")

        self.assertTrue(result)
        miner.rpc.profileset.assert_called_once_with("190MHz")

    async def test_profileset_failure_returns_false(self):
        """If RPC profileset fails, should return False."""
        miner = self._make_miner(atm_enabled=False)
        miner.rpc.profileset.side_effect = Exception("RPC error")

        result = await miner.set_profile("190MHz")

        self.assertFalse(result)
