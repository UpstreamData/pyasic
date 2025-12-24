#!/usr/bin/env python3
# mypy: ignore-errors
"""
Test script to verify Braiins serial number support.

Usage:
    python test_braiins_serials.py <miner_ip> [username] [password]

Example:
    python test_braiins_serials.py 192.168.1.100
    python test_braiins_serials.py 192.168.1.100 root root
"""

import asyncio
import sys

from pyasic.data import MinerData
from pyasic.miners.base import BaseMiner
from pyasic.miners.factory import miner_factory


async def _connect_to_miner(ip: str, username: str, password: str) -> BaseMiner | None:
    """Connect to miner and set credentials."""
    print(f"Connecting to miner at {ip}...")
    miner = await miner_factory.get_miner(ip)

    if not isinstance(miner, BaseMiner):
        print(f"❌ Failed to detect miner type at {ip}")
        return None

    print(f"✅ Detected miner: {miner.model}")
    print(f"   Firmware: {miner.firmware}\n")

    # Set credentials if needed (for BOSer)
    if miner.web is not None:
        miner.web.pwd = password
        miner.web.username = username
    if miner.rpc is not None:
        miner.rpc.pwd = password

    return miner


async def _test_miner_serial(miner: BaseMiner) -> None:
    """Test miner serial number retrieval."""
    print("1️⃣  Retrieving Miner Serial Number...")
    try:
        serial = await miner.get_serial_number()
        if serial:
            print(f"   ✅ Miner Serial: {serial}\n")
        else:
            print("   ⚠️  Miner Serial: Not available\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")


async def _test_psu_serial(miner: BaseMiner) -> None:
    """Test PSU serial number retrieval."""
    print("2️⃣  Retrieving PSU Serial Number...")
    try:
        psu_serial = await miner.get_psu_serial_number()
        if psu_serial:
            print(f"   ✅ PSU Serial: {psu_serial}\n")
        else:
            print("   ⚠️  PSU Serial: Not available\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")


def _display_miner_data(data: MinerData) -> None:
    """Display miner data including hashboard serials."""
    print("   ✅ Data retrieved successfully\n")
    print(f"   Miner IP: {data.ip}")
    print(f"   Serial Number: {data.serial_number or 'N/A'}")
    print(f"   PSU Serial Number: {data.psu_serial_number or 'N/A'}")
    print(f"   MAC Address: {data.mac or 'N/A'}")
    print(f"   Firmware: {data.fw_ver or 'N/A'}")
    print(f"   API Version: {data.api_ver or 'N/A'}")

    # Display hashboard serials
    if data.hashboards:
        print(f"\n   Hashboards ({len(data.hashboards)}):")
        for hb in data.hashboards:
            serial = f"SN: {hb.serial_number}" if hb.serial_number else "SN: N/A"
            chips = f"{hb.chips or '?'}"
            temp = f"{hb.temp or '?'}°C"
            print(f"      Slot {hb.slot}: {serial} | Chips: {chips} | Temp: {temp}")


async def test_braiins_serials(ip: str, username: str, password: str) -> bool:
    """Test serial number retrieval from a Braiins OS miner."""
    print(f"\n{'=' * 70}")
    print(f"Testing Braiins Serial Numbers on {ip}")
    print(f"{'=' * 70}\n")

    try:
        miner = await _connect_to_miner(ip, username, password)
        if miner is None:
            return False

        await _test_miner_serial(miner)
        await _test_psu_serial(miner)

        # Test 3: Get full data including hashboard serials
        print("3️⃣  Retrieving Full Miner Data (with hashboard serials)...")
        try:
            data = await miner.get_data()
            _display_miner_data(data)
            print(f"\n{'=' * 70}\n")
            return True
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            return False

    except Exception as e:
        print(f"❌ Connection failed: {e}\n")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    ip = sys.argv[1]
    username = sys.argv[2] if len(sys.argv) > 2 else "root"
    password = sys.argv[3] if len(sys.argv) > 3 else "root"

    # Run async test
    success = asyncio.run(test_braiins_serials(ip, username, password))
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
