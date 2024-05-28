import pytest
from unittest.mock import patch, mock_open
from pyasic.ssh.braiins_os import BOSMinerSSH

@pytest.fixture
def bosminer_ssh():
    return BOSMinerSSH(ip="192.168.1.100")

@pytest.mark.asyncio
async def test_upgrade_firmware_with_valid_file_location(bosminer_ssh):
    with patch("pyasic.ssh.braiins_os.os.path.exists") as mock_exists, \
         patch("pyasic.ssh.braiins_os.open", mock_open(read_data="data")) as mock_file, \
         patch("pyasic.ssh.braiins_os.requests.get") as mock_get, \
         patch.object(bosminer_ssh, "send_command") as mock_send_command:

        mock_exists.return_value = False
        file_location = "/path/to/firmware.tar.gz"

        result = await bosminer_ssh.upgrade_firmware(file_location=file_location)

        mock_send_command.assert_any_call(f"scp {file_location} root@{bosminer_ssh.ip}:/tmp/firmware.tar.gz")
        mock_send_command.assert_any_call("tar -xzf /tmp/firmware.tar.gz -C /tmp")
        mock_send_command.assert_any_call("sh /tmp/upgrade_firmware.sh")
        assert result is not None