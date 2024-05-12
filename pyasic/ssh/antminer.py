from pyasic import settings
from pyasic.ssh.base import BaseSSH


class AntminerModernSSH(BaseSSH):
    """
    Initialize an AntminerModernSSH instance.

    Args:
        ip (str): The IP address of the Antminer device.
    """

    def __init__(self, ip: str):
        super().__init__(ip)
        self.pwd = settings.get("default_antminer_ssh_password", "root")
        self.username = "miner"
