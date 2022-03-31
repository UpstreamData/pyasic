from API.bmminer import BMMinerAPI
from API.bosminer import BOSMinerAPI
from API.cgminer import CGMinerAPI
from API.btminer import BTMinerAPI
from API.unknown import UnknownAPI
import ipaddress
import asyncssh
import logging


class BaseMiner:
    def __init__(
        self,
        ip: str,
        api: BMMinerAPI or BOSMinerAPI or CGMinerAPI or BTMinerAPI or UnknownAPI,
    ) -> None:
        self.ip = ipaddress.ip_address(ip)
        self.uname = None
        self.pwd = None
        self.api = api
        self.api_type = None
        self.model = None

    async def _get_ssh_connection(self) -> asyncssh.connect:
        """Create a new asyncssh connection"""
        try:
            conn = await asyncssh.connect(
                str(self.ip),
                known_hosts=None,
                username=self.uname,
                password=self.pwd,
                server_host_key_algs=["ssh-rsa"],
            )
            return conn
        except asyncssh.misc.PermissionDenied:
            try:
                conn = await asyncssh.connect(
                    str(self.ip),
                    known_hosts=None,
                    username="admin",
                    password="admin",
                    server_host_key_algs=["ssh-rsa"],
                )
                return conn
            except Exception as e:
                logging.warning(f"{self} raised an exception: {e}")
                raise e
        except OSError:
            logging.warning(f"Connection refused: {self}")
            return None
        except Exception as e:
            logging.warning(f"{self} raised an exception: {e}")
            raise e

    async def get_board_info(self):
        return None

    async def get_config(self):
        return None

    async def get_hostname(self):
        return None

    async def get_model(self):
        return None

    async def reboot(self):
        return None

    async def restart_backend(self):
        return None

    async def send_config(self, yaml_config):
        return None
